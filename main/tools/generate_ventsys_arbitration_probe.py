"""Generate isolated HA script-engine probe; all MQTT is replaced by test text.

Writes a local file only. Install temporarily, reload helpers/scripts, run ONLY
script.ventsys_probe_run, inspect input_text.ventsys_probe_result, then remove.
Never turns on a production script, helper or physical device.
"""
import argparse
from copy import deepcopy
from pathlib import Path
import yaml
from generate_ventsys_arbitration import SOURCE, build, EXECUTOR, FIRE


def probe():
    source = build(yaml.safe_load(SOURCE.read_text(encoding='utf-8')))
    scripts = source['script']
    # Give every reference a distinct test-only ID, including the dashboard
    # cancellation target. The latter is a stub, never the live wrapper.
    renames = {name: name.replace('ventsys_', 'ventsys_probe_', 1) for name in scripts}
    renames['ventsys_dashboard_command'] = 'ventsys_probe_dashboard_command'
    def isolate(node):
        if isinstance(node, str):
            for old, new in renames.items():
                node = node.replace('script.' + old, 'script.' + new)
            return node.replace('input_boolean.ventsys_failsafe', 'input_boolean.ventsys_probe_failsafe')
        if isinstance(node, list):
            return [isolate(item) for item in node]
        if isinstance(node, dict):
            return {key: isolate(value) for key, value in node.items()}
        return node
    def no_mqtt(node, marker):
        if isinstance(node, list):
            result = []
            for item in node:
                if isinstance(item, dict) and item.get('action') == 'mqtt.publish':
                    result.extend([
                        {'action': 'input_text.set_value', 'target': {'entity_id': 'input_text.ventsys_probe_log'},
                         'data': {'value': "{{ states('input_text.ventsys_probe_log') ~ '" + marker + "' }}"}},
                        {'delay': {'milliseconds': 200 if marker == 'N' else 1}},
                    ])
                else:
                    result.append(no_mqtt(item, marker))
            return result
        if isinstance(node, dict):
            return {key: no_mqtt(value, marker) for key, value in node.items()}
        return node
    isolated = {renames[name]: no_mqtt(isolate(script), 'F' if name == FIRE else 'N')
                for name, script in scripts.items()}
    isolated[renames['ventsys_dashboard_command']] = {'sequence': [{'delay': 1}]}
    def text(entity, value):
        return {'action': 'input_text.set_value', 'target': {'entity_id': 'input_text.ventsys_probe_' + entity}, 'data': {'value': value}}
    def check(expression, message):
        return {'if': [{'condition': 'template', 'value_template': '{{ not (' + expression + ') }}'}],
                'then': [text('result', 'FAIL: ' + message), {'stop': message, 'error': True}]}
    fire_count = len(scripts[FIRE]['sequence']) - 1
    expected = 'N' + 'F' * fire_count
    isolated['ventsys_probe_run'] = {'alias': 'VentSys isolated arbitration probe — no MQTT', 'mode': 'single', 'sequence': [
        text('result', 'RUNNING'), text('log', ''),
        {'action': 'input_boolean.turn_off', 'target': {'entity_id': 'input_boolean.ventsys_probe_failsafe'}},
        {'action': 'script.' + renames['ventsys_ramp_valve'], 'data': {
            'topic': 'ventsys/main/valve1/control', 'entity_id': 'number.ventsys_probe_unused', 'target': 50}},
        check("states('input_text.ventsys_probe_log') == 'N'", 'native numeric template rejected'),
        text('log', ''),
        {'action': 'script.turn_on', 'target': {'entity_id': 'script.' + renames['ventsys_mode_purge']}},
        {'wait_template': "{{ states('input_text.ventsys_probe_log') == 'N' }}", 'timeout': '00:00:02', 'continue_on_timeout': False},
        {'action': 'script.turn_on', 'target': {'entity_id': 'script.' + renames['ventsys_mode_sealed']}},
        {'delay': {'milliseconds': 50}},
        check("states('input_text.ventsys_probe_log') == 'N'", 'normal batches interleaved'),
        {'action': 'input_boolean.turn_on', 'target': {'entity_id': 'input_boolean.ventsys_probe_failsafe'}},
        {'action': 'script.' + renames[FIRE]},
        {'delay': {'milliseconds': 300}},
        check("states('input_text.ventsys_probe_log') == '" + expected + "'", 'fire did not preempt normal execution'),
        {'action': 'script.' + renames['ventsys_mode_purge'], 'continue_on_error': True},
        check("states('input_text.ventsys_probe_log') == '" + expected + "'", 'failsafe allowed normal command'),
        text('result', 'PASS: serialized, fire preemption, failsafe blocked; no MQTT'),
    ]}
    result = {'input_text': {'ventsys_probe_log': {'max': 255, 'initial': ''},
                             'ventsys_probe_result': {'max': 255, 'initial': 'NOT RUN'}},
              'input_boolean': {'ventsys_probe_failsafe': {'initial': False}}, 'script': isolated}
    # All service actions and cancellation targets must remain in the sandbox.
    def audit(node):
        if isinstance(node, dict):
            action = node.get('action', '')
            assert not action or action.startswith('script.ventsys_probe_') or action in {
                'script.turn_on', 'script.turn_off', 'input_text.set_value', 'input_boolean.turn_on', 'input_boolean.turn_off'}
            target = node.get('target', {})
            ids = target.get('entity_id', []) if isinstance(target, dict) else []
            for entity in ([ids] if isinstance(ids, str) else ids):
                assert '.ventsys_probe_' in entity, entity
            for value in node.values(): audit(value)
        elif isinstance(node, list):
            for value in node: audit(value)
    audit(result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.write_text('# Temporary isolated probe. No production service targets or MQTT.\n' +
                          yaml.safe_dump(probe(), allow_unicode=True, sort_keys=False), encoding='utf-8')
    print('Generated isolated probe; install/run only the test-prefixed scripts.')
