"""Build the shared dispatcher runtime from the accepted mode recipes.

No network access or actuator calls. Existing script IDs remain compatible.
Generated output must replace the existing scripts package, never coexist with it.
"""
from copy import deepcopy
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'ventsys/ventsys_bundle_updated/ventsys_ha_scripts.yaml'
OUTPUT = ROOT / 'configs/home-assistant/ventsys_ha_scripts_arbitrated.yaml'
EXECUTOR = 'ventsys_normal_command'
FIRE = 'ventsys_mode_fire_safe'
NORMAL_ALLOWED = "{{ is_state('input_boolean.ventsys_failsafe', 'off') and is_state('script.ventsys_mode_fire_safe', 'off') }}"


def commands(sequence):
    """Flatten command-only recipes, rejecting unrecognized control flow.

    Former parallel target writes become ordered, direct publishes. No motion
    delays/ramping are introduced. Guards/conditions may never be silently lost.
    """
    result = []
    for entry in sequence:
        if set(entry) == {'parallel'}:
            result.extend(commands(entry['parallel']))
        elif entry.get('action') == 'mqtt.publish' and set(entry) <= {'action', 'data'}:
            data = entry['data']
            if set(data) - {'topic', 'payload', 'retain'} or data.get('retain', False):
                raise ValueError('Unsupported MQTT recipe')
            result.append({'topic': data['topic'], 'payload': str(data['payload'])})
        elif entry.get('action') == 'script.ventsys_ramp_valve' and set(entry) <= {'action', 'data'}:
            data = entry['data']
            if set(data) - {'topic', 'entity_id', 'target'}:
                raise ValueError('Unsupported valve recipe')
            result.append({'topic': data['topic'], 'payload': str(data['target'])})
        else:
            raise ValueError('Unsupported recipe action/control flow')
    return result


def build(source):
    recipes = source['script']
    modes = {name: commands(script['sequence']) for name, script in recipes.items()
             if name.startswith('ventsys_mode_')}
    if FIRE not in modes or len(modes) != 13:
        raise ValueError('Unexpected mode inventory')
    valve_topics = sorted({command['topic'] for command_list in modes.values()
                           for command in command_list
                           if command['topic'].endswith('/control') and '/fan/' not in command['topic']
                           and '/spray-fan/' not in command['topic']})
    fan_topics = ['ventsys/fan/control', 'ventsys/spray-fan/control']
    speed_topics = ['ventsys/fan/percent', 'ventsys/spray-fan/percent']
    # Validate the whole request before any publish. Explicitly bound its size,
    # allowed topics and canonical integer strings; never accept arbitrary MQTT.
    invalid = """{% set ns = namespace(bad=false) %}
{% if commands is not defined or commands is string or commands is mapping or commands is not sequence %}true
{% elif commands | count < 1 or commands | count > 12 %}true
{% else %}{% for c in commands %}
 {% if c is not mapping or c.keys() | list | sort != ['payload','topic'] %}{% set ns.bad=true %}
 {% elif c.topic in fan_topics %}{% if c.payload not in ['on','off'] %}{% set ns.bad=true %}{% endif %}
 {% elif c.topic in valve_topics or c.topic in speed_topics %}
  {% if (c.payload is not string and c.payload is not integer) or c.payload | int(-1) < 0 or c.payload | int(-1) > 100 or (c.payload is string and c.payload | int(-1) | string != c.payload) %}{% set ns.bad=true %}{% endif %}
 {% else %}{% set ns.bad=true %}{% endif %}
{% endfor %}{{ ns.bad }}{% endif %}"""
    scripts = {EXECUTOR: {
        'alias': 'VentSys — shared normal command dispatcher', 'mode': 'single',
        'max_exceeded': 'warning',
        'sequence': [
            {'variables': {'valve_topics': valve_topics, 'fan_topics': fan_topics, 'speed_topics': speed_topics}},
            {'if': [{'condition': 'template', 'value_template': invalid}],
             'then': [{'stop': 'Invalid VentSys command batch', 'error': True}]},
            {'repeat': {'for_each': '{{ commands }}', 'sequence': [
                {'if': [{'condition': 'template', 'value_template': '{{ not (' + NORMAL_ALLOWED[3:-3] + ') }}'}],
                 'then': [{'stop': 'Failsafe active/unknown or fire response running', 'error': True}]},
                {'action': 'mqtt.publish', 'data': {'topic': '{{ repeat.item.topic }}',
                 'payload': '{{ repeat.item.payload }}', 'retain': False}},
            ]}},
        ],
    }}
    for name, batch in modes.items():
        script = {key: deepcopy(value) for key, value in recipes[name].items() if key != 'sequence'}
        script['mode'] = 'single'
        if name == FIRE:
            # Stop normal publishes first. Fire commands deliberately bypass the
            # normal failsafe guard and are not routed through a cancellable helper.
            stop_targets = ['script.' + EXECUTOR, 'script.ventsys_dashboard_command',
                            'script.ventsys_ramp_valve'] + ['script.' + key for key in modes if key != FIRE]
            script['sequence'] = [
                {'action': 'script.turn_off', 'target': {'entity_id': stop_targets}},
                *[{'action': 'mqtt.publish', 'data': {**command, 'retain': False}} for command in batch],
            ]
        else:
            script['sequence'] = [{'action': 'script.' + EXECUTOR, 'data': {'commands': batch}}]
        scripts[name] = script
    helper = deepcopy(recipes['ventsys_ramp_valve'])
    helper['sequence'] = [{'action': 'script.' + EXECUTOR, 'data': {'commands': [
        {'topic': '{{ topic }}', 'payload': '{{ target | int | string }}'}]}}]
    scripts['ventsys_ramp_valve'] = helper
    return {'script': scripts}


def build_dashboard(source):
    """Route direct dashboard commands through the same executor as mode calls."""
    result = deepcopy(source)
    dispatch = next(step for step in result['script']['ventsys_dashboard_command']['sequence'] if 'choose' in step)
    if dispatch['default'][0]['action'] == 'script.' + EXECUTOR:
        return result
    if dispatch['default'][0]['action'] != 'mqtt.publish':
        raise ValueError('Unexpected dashboard command schema')
    data = dispatch['default'][0]['data']
    dispatch['default'] = [{'action': 'script.' + EXECUTOR, 'data': {'commands': [
        {'topic': data['topic'], 'payload': data['payload']}]}}]
    return result


if __name__ == '__main__':
    document = build(yaml.safe_load(SOURCE.read_text(encoding='utf-8')))
    OUTPUT.write_text('# Generated by tools/generate_ventsys_arbitration.py. Replaces live ventsys_ha_scripts.yaml.\n' +
                      yaml.safe_dump(document, allow_unicode=True, sort_keys=False, width=120), encoding='utf-8')
    print('Generated arbitrated scripts runtime; no live files changed.')
