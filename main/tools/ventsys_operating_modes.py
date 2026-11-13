"""Independent operating intents and exhaust-path planning. No I/O or actuation."""
from itertools import product
from copy import deepcopy

MODES = ('off', 'enclosure', 'print', 'purge')
EMPTY = {'fdm': 'off', 'sla': 'off', 'booth': 'off'}
PURGE_STRENGTHS = {2: 'Low', 4: 'Moderate', 6: 'Medium', 8: 'High', 10: 'Max'}


def validate(state):
    if not isinstance(state, dict) or set(state) != set(EMPTY):
        raise ValueError('Invalid operating state')
    if any(state[z] not in MODES for z in ('fdm', 'sla')) or state['booth'] not in ('off', 'enclosure'):
        raise ValueError('Invalid operating mode')
    return dict(state)


def key(state):
    validate(state)
    return '|'.join(state[z] for z in EMPTY)


def requirements(state):
    """Targets owned by active intents; inactive/unmanaged branches are omitted."""
    validate(state)
    targets = {}
    for zone in ('fdm', 'sla'):
        mode = state[zone]
        if mode != 'off':
            targets.update({zone + '_branch': 100,
                            zone + '_360': 60 if mode in ('enclosure', 'purge') else 30,
                            zone + '_print': 100 if mode in ('print', 'purge') else 0})
    if state['sla'] != 'off' or state['booth'] != 'off':
        targets['main1'] = 100
    if state['booth'] != 'off':
        targets.update(main2=100, fan_booth='on')
    if any(value != 'off' for value in state.values()):
        targets['fan_main'] = 'on'
    return targets


def transition(previous, zone, mode):
    previous = validate(previous)
    if zone not in ('fdm', 'sla', 'both', 'booth', 'all') or mode not in MODES:
        raise ValueError('Invalid operating request')
    if zone == 'booth' and mode not in ('off', 'enclosure') or zone == 'all' and mode != 'off':
        raise ValueError('Invalid operating request')
    desired = dict(previous)
    for item in (('fdm', 'sla') if zone == 'both' else tuple(EMPTY) if zone == 'all' else (zone,)):
        desired[item] = mode
    needed = requirements(desired)
    targets = dict(needed)
    # Release only resources previously owned by an active intent. Starting FDM
    # must never close a manual/unmanaged SLA branch, MAIN-1 or Booth path.
    for item in ('fdm', 'sla'):
        if previous[item] != 'off' and desired[item] == 'off':
            targets.update({item + '_branch': 0, item + '_print': 0, item + '_360': 30})
    old = requirements(previous)
    for item in ('main1', 'main2', 'fan_booth', 'fan_main'):
        if item in old and item not in needed:
            targets[item] = 'off' if item.startswith('fan_') else 0
    # Explicit Stop all also seals branches when no previous intent is known.
    if zone == 'all':
        targets = {**{z + suffix: value for z in ('fdm', 'sla')
                       for suffix, value in (('_branch', 0), ('_print', 0), ('_360', 30))},
                   'main1': 0, 'main2': 0, 'fan_main': 'off', 'fan_booth': 'off'}
    # Fan-off first; open inlets/routes next; start fans after open reports;
    # close superseded paths last. Each phase is separately report-confirmed.
    phases = [{k: v for k, v in targets.items() if k.startswith('fan_') and v == 'off'},
              {k: v for k, v in targets.items() if not k.startswith('fan_') and v in (60, 100)},
              {k: v for k, v in targets.items() if k.startswith('fan_') and v == 'on'},
              {k: v for k, v in targets.items() if not k.startswith('fan_') and v in (0, 30)}]
    return {'desired': desired, 'targets': targets, 'phases': [p for p in phases if p]}


def with_strength(plan, previous, zone, mode, strength=None):
    """Apply independently owned purge levels to a base path plan.

    Owner-approved requested mapping: physical labels 2/4/6/8/10 -> HA
    20/40/60/80/100 percent. Physical calibration remains pending.
    """
    if mode == 'purge':
        if type(strength) is not int or strength not in PURGE_STRENGTHS:
            raise ValueError('Choose a purge strength')
    elif strength is not None:
        raise ValueError('Strength only applies to purge')
    plan = deepcopy(plan)
    for item in ('fdm', 'sla'):
        active = plan['desired'][item] == 'purge'
        selected = zone in (item, 'both')
        level = strength if active and selected else previous.get(item + '_strength', 6) if active else 0
        if active and (type(level) is not int or level not in PURGE_STRENGTHS):
            raise ValueError('Invalid saved purge strength')
        plan['desired'][item + '_strength'] = level
    percent = max(plan['desired'][item + '_strength'] for item in ('fdm', 'sla')) * 10
    if percent:
        plan['targets']['fan_main_speed'] = percent
        # Percent command also starts this firmware's fan: only send it in the
        # fan phase, after every new open-path controller report was received.
        for index, phase in enumerate(plan['phases']):
            if phase.get('fan_main') == 'on':
                plan['phases'][index] = {'fan_main_speed': percent, **phase}
                break
    return plan


STATES = {key(state): state for f, s, b in product(MODES, MODES, ('off', 'enclosure'))
          for state in [{'fdm': f, 'sla': s, 'booth': b}]}
REQUESTS = [(z, m) for z in ('fdm', 'sla', 'both') for m in MODES] + [('booth', 'off'), ('booth', 'enclosure'), ('all', 'off')]


def setup_targets(zone, mode):
    """Valve-only bench targets, never fan commands or active mode intents."""
    previous = dict(EMPTY)
    if mode == 'off':
        for item in (('fdm','sla') if zone == 'both' else tuple(EMPTY) if zone == 'all' else (zone,)):
            previous[item] = 'enclosure'
    return {k: v for k, v in transition(previous, zone, mode)['targets'].items() if not k.startswith('fan_')}


TEST_TARGETS = {z + ':' + m: setup_targets(z, m) for z, m in REQUESTS}
