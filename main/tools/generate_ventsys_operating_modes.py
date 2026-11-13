"""Generate guarded, composable operating mode package and browser contract.

Run after generate_ventsys_dashboard_contract.py and generate_ventsys_arbitration.py.
Only writes local source artifacts; never connects to Home Assistant.
"""
import json
from pathlib import Path
import yaml
from ventsys_operating_modes import EMPTY, STATES, REQUESTS, requirements, transition, TEST_TARGETS

ROOT = Path(__file__).resolve().parents[1]
HELPER = 'input_text.ventsys_operating_state'
MANAGER = 'ventsys_set_operating_mode'


def native(node):
    if isinstance(node, str) and '{%' in node and '{%-' not in node:
        return node.replace('{%', '{%-').replace('%}', '-%}').replace('{{', '{{-').replace('}}', '-}}')
    if isinstance(node, list):
        return [native(value) for value in node]
    if isinstance(node, dict):
        return {key: native(value) for key, value in node.items()}
    return node


def build():
    dashboard = yaml.safe_load((ROOT / 'configs/home-assistant/ventsys_dashboard_package.yaml').read_text(encoding='utf-8'))
    sequence = dashboard['script']['ventsys_dashboard_command']['sequence']
    controls = sequence[0]['variables']['controls']
    plans = {old: {z + ':' + m: transition(state, z, m) for z, m in REQUESTS} for old, state in STATES.items()}
    required = {old: requirements(state) for old, state in STATES.items()}
    # Use the same availability/range/report checks as individual commands.
    availability = sequence[5]['variables']['blocked']
    confirmed = sequence[-1]['wait_template']
    allowed = "{{ is_state('input_boolean.ventsys_failsafe','off') and is_state('script.ventsys_mode_fire_safe','off') }}"
    stop = lambda message: {'stop': message, 'error': True}
    def guard(test, message):
        return {'if': [{'condition': 'template', 'value_template': test}], 'then': [stop(message)]}
    # No initial value: HA restores the last requested intents after restart.
    # An empty helper is the first-install default; it does not issue commands.
    script = {'alias': 'VentSys — set independent operating mode', 'mode': 'single', 'max_exceeded': 'error',
              'fields': {**{k: {'required': True} for k in ('zone', 'operation', 'revision')}, 'strength': {'description': 'Purge level: 2,4,6,8,10; maps to 20,40,60,80,100 percent pending calibration'}}, 'sequence': [
        {'variables': {'controls': controls, 'plans': plans}},
        {'variables': {'current': "{{ states('" + HELPER + "') | from_json({'fdm':'off','sla':'off','booth':'off','revision':0}) }}"}},
        {'variables': {'current_key': "{{ current.fdm | default('invalid') ~ '|' ~ current.sla | default('invalid') ~ '|' ~ current.booth | default('invalid') }}",
                       'request_key': "{{ zone | default('invalid') ~ ':' ~ operation | default('invalid') }}"}},
        guard("{{ not (" + allowed[3:-3] + ") }}", 'Failsafe active/unknown or fire response running'),
        guard("{{ not is_state('script.ventsys_normal_command','off') or not is_state('script.ventsys_dashboard_command','off') or not is_state('script.ventsys_record_intake_reference','off') }}", 'Another command is running'),
        guard("{{ current_key not in plans or request_key not in plans.get(current_key,{}) or revision is not integer or revision != current.revision | default(-1) or states('input_text.ventsys_operating_state') not in ['', 'unknown'] and states('input_text.ventsys_operating_state') | from_json(none) is none or operation == 'purge' and (strength | default(none) is not integer or strength not in [2,4,6,8,10]) or operation != 'purge' and strength | default(none) is not none }}", 'Invalid or stale mode request; choose a valid purge strength and refresh controller state'),
        {'variables': {'plan': """{% set base=plans[current_key][request_key] %}
{% set f=(strength if zone in ['fdm','both'] else current.fdm_strength | default(6)) if base.desired.fdm == 'purge' else 0 %}
{% set s=(strength if zone in ['sla','both'] else current.sla_strength | default(6)) if base.desired.sla == 'purge' else 0 %}
{% set percent=([f,s] | max) * 10 %}{% set ns=namespace(phases=[]) %}
{% for phase in base.phases %}{% set ns.phases=ns.phases + [dict({'fan_main_speed':percent}, **phase) if percent > 0 and phase.get('fan_main') == 'on' else phase] %}{% endfor %}
{{ {'desired':dict(base.desired,fdm_strength=f,sla_strength=s), 'targets':dict(base.targets, **({'fan_main_speed':percent} if percent > 0 else {})), 'phases':ns.phases} }}"""}},
        {'variables': {'expected': '{{ plan.targets }}'}},
        {'variables': {'blocked': availability}},
        guard('{{ blocked | trim != "" }}', '{{ blocked }}'),
        # Do not guess a speed. Fan-on with a zero/unknown retained speed cannot
        # establish a usable extraction request.
        guard("{% set ns=namespace(bad=false) %}{% for key,value in expected.items() %}{% if key.startswith('fan_') and value == 'on' and key ~ '_speed' not in expected %}{% set report=states[controls[key].entity] %}{% if report is none or report.attributes.get('percentage',0) | float(0) <= 0 %}{% set ns.bad=true %}{% endif %}{% endif %}{% endfor %}{{ ns.bad }}", 'Set a nonzero extraction fan speed before starting this mode'),
        {'action': 'input_text.set_value', 'target': {'entity_id': HELPER}, 'data': {'value': "{{ dict(plan.desired, revision=current.revision + 1) | to_json }}"}},
        {'action': 'input_text.set_value', 'target': {'entity_id': 'input_text.ventsys_operating_result'}, 'data': {'value': 'Applying; controller reports pending'}},
        {'repeat': {'for_each': '{{ plan.phases }}', 'sequence': [
            guard("{{ not (" + allowed[3:-3] + ") }}", 'Emergency interrupted operating transition'),
            {'variables': {'expected': '{{ repeat.item }}'}},
            {'variables': {'blocked': availability}},
            guard('{{ blocked | trim != "" }}', '{{ blocked }}'),
            {'action': 'script.ventsys_normal_command', 'data': {'operating': True, 'commands': "{% set ns=namespace(batch=[]) %}{% for key,value in expected.items() %}{% set speed=key.endswith('_speed') %}{% set device=controls[key[:-6] if speed else key] %}{% set ns.batch=ns.batch + [{'topic':device.speedTopic if speed else device.topic,'payload':value | string}] %}{% endfor %}{{ ns.batch }}"}},
            {'wait_template': confirmed, 'timeout': '00:00:08', 'continue_on_timeout': True},
            {'if': [{'condition': 'template', 'value_template': '{{ not wait.completed }}'}], 'then': [
                {'action': 'input_text.set_value', 'target': {'entity_id': 'input_text.ventsys_operating_result'}, 'data': {'value': 'Failed: controller report timeout; requested intents retained; retry to reconcile'}},
                stop('Operating transition stopped: controller report timeout')]},
        ]}},
        guard("{{ not (" + allowed[3:-3] + ") }}", 'Emergency interrupted operating transition'),
        {'action': 'input_text.set_value', 'target': {'entity_id': 'input_text.ventsys_operating_result'}, 'data': {'value': 'Targets confirmed by controller reports'}},
    ]}
    test_script = {'alias':'VentSys — setup valve test (not ventilation)', 'mode':'single', 'max_exceeded':'error',
                   'fields':{key:{'required':True} for key in ('zone','operation','revision','included')}, 'sequence':[
        {'variables':{'controls':controls,'test_targets':TEST_TARGETS}},
        {'variables':{'current':"{{ states('input_text.ventsys_operating_state') | from_json({'fdm':'off','sla':'off','booth':'off','revision':0}) }}",
                      'request_key':"{{ zone | default('invalid') ~ ':' ~ operation | default('invalid') }}"}},
        guard("{{ not (" + allowed[3:-3] + ") }}", 'Failsafe/fire blocks setup tests'),
        guard("{{ not is_state('script.ventsys_set_operating_mode','off') or not is_state('script.ventsys_normal_command','off') or not is_state('script.ventsys_dashboard_command','off') or not is_state('script.ventsys_record_intake_reference','off') }}", 'Another command is running'),
        guard("{{ current.fdm | default('invalid') != 'off' or current.sla | default('invalid') != 'off' or current.booth | default('invalid') != 'off' or revision is not integer or revision != current.revision | default(-1) }}", 'Stop operating intents before setup testing; stale requests are rejected'),
        guard("{{ is_state('fan.inline_fan','on') or is_state('fan.spray_booth_fan','on') }}", 'Stop running fans before valve setup testing'),
        guard("{% set ns=namespace(bad=false) %}{% if request_key not in test_targets or included is not defined or included is string or included is mapping or included is not sequence %}true{% elif included | count < 1 or included | count > 8 or included | unique | list | count != included | count %}true{% else %}{% for key in included %}{% if key is not string or key not in test_targets[request_key] %}{% set ns.bad=true %}{% endif %}{% endfor %}{{ ns.bad }}{% endif %}", 'Invalid setup valve subset'),
        {'variables':{'expected':"{% set ns=namespace(result={}) %}{% for key in included %}{% set ns.result=dict(ns.result,**{key:test_targets[request_key][key]}) %}{% endfor %}{{ ns.result }}"}},
        {'variables':{'blocked':availability}},
        guard('{{ blocked | trim != "" }}','{{ blocked }}'),
        {'action':'script.ventsys_normal_command','data':{'testing':True,'commands':"{% set ns=namespace(batch=[]) %}{% for key,value in expected.items() %}{% set ns.batch=ns.batch + [{'topic':controls[key].topic,'payload':value | string}] %}{% endfor %}{{ ns.batch }}"}},
        {'wait_template':confirmed,'timeout':'00:00:08','continue_on_timeout':False},
    ]}
    package = native({'input_text': {
        'ventsys_operating_state': {'name': 'VentSys requested operating intents', 'max': 255},
        'ventsys_operating_result': {'name': 'VentSys operating result', 'max': 255},
    }, 'script': {MANAGER: script, 'ventsys_test_valves':test_script}})
    package['script'][MANAGER]['sequence'][4]['if'][0]['value_template'] = "{{ not is_state('script.ventsys_normal_command','off') or not is_state('script.ventsys_dashboard_command','off') or not is_state('script.ventsys_test_valves','off') or not is_state('script.ventsys_record_intake_reference','off') }}"
    # Block manual/legacy batches that contradict a currently active intent.
    # Invalid/missing state after installation is fail-closed in the dispatcher.
    conflict = native("""{% set saved=states('input_text.ventsys_operating_state') | from_json({'fdm':'off','sla':'off','booth':'off'}) %}
{% set active_key=saved.fdm | default('invalid') ~ '|' ~ saved.sla | default('invalid') ~ '|' ~ saved.booth | default('invalid') %}
{% set raw=states('input_text.ventsys_operating_state') %}
{% set owner=operating | default(false) %}
{% set tester=testing | default(false) %}
{% set ns=namespace(bad=not is_state('script.ventsys_record_intake_reference','off') or active_key not in operating_required or raw == 'unavailable' or raw not in ['', 'unknown'] and raw | from_json(none) is none or owner is not boolean or owner != is_state('script.ventsys_set_operating_mode','on') or states('script.ventsys_set_operating_mode') not in ['on','off']) %}
{% if tester is not boolean or tester != is_state('script.ventsys_test_valves','on') or states('script.ventsys_test_valves') not in ['on','off'] or tester and owner %}{% set ns.bad=true %}{% endif %}
{% if tester and (is_state('fan.inline_fan','on') or is_state('fan.spray_booth_fan','on') or saved.fdm | default('invalid') != 'off' or saved.sla | default('invalid') != 'off' or saved.booth | default('invalid') != 'off') %}{% set ns.bad=true %}{% endif %}
{% if tester %}{% for c in commands %}{% if c.topic not in valve_topics %}{% set ns.bad=true %}{% endif %}{% endfor %}{% endif %}
{% set f=saved.fdm_strength | default(6) if saved.fdm | default('off') == 'purge' else 0 %}
{% set s=saved.sla_strength | default(6) if saved.sla | default('off') == 'purge' else 0 %}
{% if f is not integer or s is not integer or f not in [0,2,4,6,8,10] or s not in [0,2,4,6,8,10] %}{% set ns.bad=true %}{% endif %}
{% set percent=([f,s] | max) * 10 %}
{% for c in commands %}{% if percent > 0 and c.topic == operating_controls.fan_main.speedTopic and c.payload | int(-1) != percent %}{% set ns.bad=true %}{% endif %}{% endfor %}
{% if active_key in operating_required %}{% for c in commands %}{% for key,value in operating_required[active_key].items() %}
{% if c.topic == operating_controls[key].topic and c.payload | string != value | string %}{% set ns.bad=true %}{% endif %}
{% if key.startswith('fan_') and value == 'on' and c.topic == operating_controls[key].speedTopic and c.payload | int(0) <= 0 %}{% set ns.bad=true %}{% endif %}
{% endfor %}{% endfor %}{% endif %}{{ ns.bad }}""")
    runtime_path = ROOT / 'configs/home-assistant/ventsys_ha_scripts_arbitrated.yaml'
    runtime = yaml.safe_load(runtime_path.read_text(encoding='utf-8'))
    executor = runtime['script']['ventsys_normal_command']['sequence']
    executor[0]['variables'].update(operating_required=required, operating_controls=controls)
    executor.insert(2, guard(conflict, 'Manual command conflicts with an active operating mode; stop that mode first'))
    # Recheck conflicts between publishes too: a concurrently accepted intent
    # cannot be undone by the remainder of an earlier normal batch.
    executor[3]['repeat']['sequence'].insert(1, guard(conflict, 'Operating intent changed; remaining commands blocked'))
    for name, recipe in runtime['script'].items():
        if not name.startswith('ventsys_mode_') or name == 'ventsys_mode_fire_safe':
            continue
        suffix = name.removeprefix('ventsys_mode_')
        if suffix in ('sealed', 'purge'):
            zone, operation = ('all', 'off') if suffix == 'sealed' else ('both', 'purge')
        elif suffix in ('booth', 'booth_seal'):
            zone, operation = 'booth', 'enclosure' if suffix == 'booth' else 'off'
        else:
            zone, operation = suffix.split('_', 1)
            operation = 'off' if operation == 'seal' else operation
        recipe['sequence'] = [{'action': 'script.' + MANAGER, 'data': {
            'zone': zone, 'operation': operation,
            **({'strength': '{{ strength | default(6) }}'} if operation == 'purge' else {}),
            'revision': "{{ (states('" + HELPER + "') | from_json({'revision':0})).revision | default(0) }}"}}]
    fire = runtime['script']['ventsys_mode_fire_safe']['sequence']
    fire[0]['target']['entity_id'].append('script.' + MANAGER)
    fire[0]['target']['entity_id'].append('script.ventsys_test_valves')
    fire[0]['target']['entity_id'].append('script.ventsys_record_intake_reference')
    # Retire old partial/global dashboard mode requests: legacy scripts now have
    # different composable semantics. Old cached cards must refresh first.
    sequence.insert(0, guard("{{ kind | default('') == 'mode' }}", 'Refresh dashboard to use independent operating modes'))
    sequence.insert(1, guard("{{ not is_state('script.ventsys_set_operating_mode','off') or not is_state('script.ventsys_test_valves','off') or not is_state('script.ventsys_record_intake_reference','off') }}", 'Operating mode transition, reference recording or setup test is running/unavailable; manual commands blocked'))
    return package, runtime, dashboard, plans


if __name__ == '__main__':
    package, runtime, dashboard, plans = build()
    for name, data in [('ventsys_operating_modes.yaml', package), ('ventsys_ha_scripts_arbitrated.yaml', runtime), ('ventsys_dashboard_package.yaml', dashboard)]:
        (ROOT / 'configs/home-assistant' / name).write_text('# Generated operating-mode integration. No boot actuation.\n' + yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120), encoding='utf-8')
    asset = ROOT / 'dashboards/ventsys-modes.mjs'
    old = asset.read_text(encoding='utf-8').split('export const OPERATING_PLANS =')[0]
    asset.write_text(old + 'export const OPERATING_PLANS = ' + json.dumps(plans, separators=(',', ':')) + ';\n', encoding='utf-8')
    print('Generated independent operating intents, transition phases and backend guards; no live changes.')
