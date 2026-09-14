"""Scenario and capacity arithmetic; offline, standard library only.

No estimates are embedded here: engineering inputs and provenance belong in JSON.
"""
import math


def num(obj, key, low=0, high=None, integer=False):
    if not isinstance(obj, dict):
        raise ValueError(f'{key}: parent object required')
    value = obj.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{key}: finite number required')
    if value < low or (high is not None and value > high) or (integer and value != int(value)):
        raise ValueError(f'{key}: out of range or noninteger')
    return value


def positive(obj, key):
    value = num(obj, key)
    if value <= 0:
        raise ValueError(f'{key}: positive value required')
    return value


def fraction(obj, key):
    value = num(obj, key, 0, 1)
    if value >= 1:
        raise ValueError(f'{key}: must be less than one')
    return value


def label(obj, key):
    if not isinstance(obj, dict):
        raise ValueError(f'{key}: parent object required')
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{key}: nonempty string required')
    return value


def indexed(items, name):
    if not isinstance(items, list) or not items:
        raise ValueError(f'{name}: nonempty list required')
    result = {}
    for obj in items:
        if not isinstance(obj, dict):
            raise ValueError(f'{name}: objects required')
        key = label(obj, 'id')
        if key in result:
            raise ValueError(f'{name}: duplicate id {key}')
        result[key] = obj
    return result


def ids(values, known, name):
    if not isinstance(values, list) or not values or any(not isinstance(x, str) for x in values):
        raise ValueError(f'{name}: nonempty string list required')
    if len(values) != len(set(values)) or any(x not in known for x in values):
        raise ValueError(f'{name}: duplicate or unknown reference')
    return values


def scenario_budget(model):
    if not isinstance(model, dict):
        raise ValueError('traffic must be an object')
    streams = indexed(model.get('streams'), 'streams')
    hops = indexed(model.get('hops'), 'hops')
    scenarios = indexed(model.get('scenarios'), 'scenarios')
    rates = {}
    for key, stream in streams.items():
        label(stream, 'port')
        label(stream, 'profile')
        rates[key] = (num(stream, 'width', 1, integer=True) * num(stream, 'height', 1, integer=True)
                      * positive(stream, 'fps') * positive(stream, 'bits_per_pixel'))
        path = ids(stream.get('path'), hops, f'{key}.path')
        vertices = [label(hops[path[0]], 'from')]
        for hop_id in path:
            hop = hops[hop_id]
            if label(hop, 'from') != vertices[-1]:
                raise ValueError(f'{key}: discontinuous route')
            vertices.append(label(hop, 'to'))
        if len(vertices) != len(set(vertices)):
            raise ValueError(f'{key}: cyclic route')
    for hop in hops.values():
        positive(hop, 'capacity_bps')
        num(hop, 'packet_factor', 1)
        if num(hop, 'coding_efficiency', 0, 1) <= 0:
            raise ValueError('coding_efficiency must be positive')
        fraction(hop, 'reserve_fraction')
        num(hop, 'stall_seconds')
        label(hop, 'buffer_owner')
        label(hop, 'capacity_basis')
    results = []
    used_streams = set()
    for sid, scenario in scenarios.items():
        active = ids(scenario.get('active_streams'), streams, f'{sid}.active_streams')
        label(scenario, 'rationale')
        sink = label(scenario, 'required_sink')
        ports = [streams[s]['port'] for s in active]
        if len(ports) != len(set(ports)):
            raise ValueError(f'{sid}: multiple profiles on one physical port; model an explicit aggregate instead')
        if any(hops[streams[s]['path'][-1]]['to'] != sink for s in active):
            raise ValueError(f'{sid}: route does not reach required sink')
        used_streams.update(active)
        rows = []
        for hid, hop in hops.items():
            routed = [s for s in active if hid in streams[s]['path']]
            if not routed:
                continue
            payload = sum(rates[s] for s in routed)
            required = payload * hop['packet_factor'] / hop['coding_efficiency']
            capacity = hop['capacity_bps']
            usable = capacity * (1 - hop['reserve_fraction'])
            per_stream = {s: math.ceil(rates[s] * hop['stall_seconds'] / 8) for s in routed}
            rows.append({'hop': hid, 'streams': routed, 'payload_bps': payload,
                         'required_wire_bps': required, 'capacity_bps': capacity,
                         'headroom_fraction': 1 - required / capacity,
                         'reserved_capacity_utilization': required / usable,
                         'minimum_capacity_bps': required / (1 - hop['reserve_fraction']),
                         'fits_reserved_capacity': required <= usable,
                         'buffer_owner': hop['buffer_owner'], 'stall_buffer_bytes_by_stream': per_stream,
                         'minimum_payload_buffer_bytes': sum(per_stream.values())})
        bottleneck = max(rows, key=lambda row: row['reserved_capacity_utilization'])
        results.append({'scenario': sid, 'concurrent_ports': ports,
                        'payload_bps': sum(rates[s] for s in active), 'hops': rows,
                        'bottleneck_hop': bottleneck['hop'],
                        'failing_hops': [row['hop'] for row in rows if not row['fits_reserved_capacity']]})
    if used_streams != set(streams):
        raise ValueError('every stream/profile must participate in a scenario')
    worst = {}
    for result in results:
        for row in result['hops']:
            if row['hop'] not in worst or row['reserved_capacity_utilization'] > worst[row['hop']]['reserved_capacity_utilization']:
                worst[row['hop']] = dict(row, scenario=result['scenario'])
    if set(worst) != set(hops):
        raise ValueError('unused hop: remove it or define its scenario')
    return {'schema_version': 2, 'physical_ports': sorted({s['port'] for s in streams.values()}),
            'max_concurrent_ports': max(len(s['concurrent_ports']) for s in results),
            'scenarios': results, 'worst_by_hop': worst,
            'fits_reserved_capacity': all(not s['failing_hops'] for s in results),
            'limitations': 'Active pixels; no implicit blanking, compression or multicast. Factors are hop-local relative to payload. Buffers assume zero service and exclude burst/metadata. Each quantity has its own worst scenario. Declared capacities are not measurements performed by this tool.'}


def resource(model, traffic):
    if not isinstance(model, dict):
        raise ValueError('resource input must be an object')
    budget = scenario_budget(traffic)
    label(model, 'evidence_scope')
    for key in ('buffer', 'production', 'power', 'external_memory'):
        if key in model and not isinstance(model[key], dict):
            raise ValueError(f'{key}: object required')
    ports = indexed(model.get('ports'), 'ports')
    if set(ports) != set(budget['physical_ports']):
        raise ValueError('resource ports must exactly cover traffic physical ports')
    channel_totals = {}
    for port in ports.values():
        kind = label(port, 'resource_type')
        count = num(port, 'lanes', 0, integer=True)
        channel_totals[kind] = channel_totals.get(kind, 0) + count
    for extra in model.get('additional_channels', []):
        label(extra, 'reason')
        kind = label(extra, 'resource_type')
        channel_totals[kind] = channel_totals.get(kind, 0) + num(extra, 'count', 0, integer=True)

    io = []
    for group in indexed(model.get('io_groups'), 'io_groups').values():
        positive(group, 'vccio_v')
        label(group, 'bank_class')
        pins = num(group, 'pins', 1, integer=True)
        usable = num(group, 'pins_per_bank', 1, integer=True) * (1 - fraction(group, 'reserve_fraction'))
        io.append({'group': group['id'], 'vccio_v': group['vccio_v'],
                   'bank_class': group['bank_class'], 'minimum_banks': math.ceil(pins / usable)})

    util = positive(model, 'maximum_utilization')
    if util > 1:
        raise ValueError('maximum_utilization must be <= 1')
    totals = {key: [0, 0] for key in ('lut', 'ff', 'dsp')}
    for block in indexed(model.get('functions'), 'functions').values():
        count = num(block, 'instances', 1, integer=True)
        if block.get('evidence_type') not in ('ASSUMPTION', 'MEASURED', 'VENDOR_ESTIMATE'):
            raise ValueError('function evidence_type required')
        label(block, 'basis')
        for key in totals:
            interval = block.get(key)
            if not isinstance(interval, list) or len(interval) != 2:
                raise ValueError(f'{key}: [low, high] required')
            low = num({'v': interval[0]}, 'v', integer=True)
            high = num({'v': interval[1]}, 'v', low, integer=True)
            totals[key][0] += low * count
            totals[key][1] += high * count
    logic = {key: {'estimated_interval': value, 'minimum_device_capacity': math.ceil(value[1] / util)}
             for key, value in totals.items()}

    buffer = model.get('buffer', {})
    hid = label(buffer, 'hop')
    if hid not in budget['worst_by_hop']:
        raise ValueError('buffer hop not in traffic')
    if budget['worst_by_hop'][hid]['buffer_owner'] != label(buffer, 'owner'):
        raise ValueError('buffer owner does not match traffic')
    burst = num(buffer, 'burst_bytes_per_port', integer=True)
    metadata = num(buffer, 'metadata_factor', 1)
    queue_bytes = {port: 0 for port in ports}
    stream_map = {stream['id']: stream for stream in traffic['streams']}
    peak_payload = 0
    for scenario in budget['scenarios']:
        for row in scenario['hops']:
            if row['hop'] == hid:
                peak_payload = max(peak_payload, row['payload_bps'])
                for stream, size in row['stall_buffer_bytes_by_stream'].items():
                    port = stream_map[stream]['port']
                    queue_bytes[port] = max(queue_bytes[port], math.ceil((size + burst) * metadata))
    queue_bytes = {key: value for key, value in queue_bytes.items() if value}
    memory = []
    def auxiliary_pools(option):
        rows = []
        for pool in option.get('auxiliary_pools', []):
            required = math.ceil(num(pool, 'allocated_blocks', 0, integer=True) / util)
            available = num(pool, 'available_blocks', 0, integer=True)
            rows.append({'id': label(pool, 'id'), 'minimum_device_blocks': required,
                         'available_blocks': available, 'fits_candidate': available >= required})
        return rows
    for option in indexed(model.get('memory_options'), 'memory_options').values():
        nominal = num(option, 'nominal_block_bits', 1, integer=True)
        usable = num(option, 'usable_block_bits', 1, nominal, integer=True)
        packing = positive(option, 'packing_efficiency')
        if packing > 1:
            raise ValueError('packing_efficiency must be <= 1')
        fixed = num(option, 'fixed_blocks', integer=True)
        available = num(option, 'available_blocks', 1, integer=True)
        allocation = {port: math.ceil(size * 8 / (usable * packing)) for port, size in queue_bytes.items()}
        allocated = sum(allocation.values()) + fixed
        minimum = math.ceil(allocated / util)
        label(option, 'mapping_limitations')
        auxiliary = auxiliary_pools(option)
        memory.append({'option': option['id'], 'blocks_by_queue': allocation,
                       'fixed_blocks': fixed, 'allocated_blocks': allocated,
                       'minimum_device_blocks': minimum, 'available_blocks': available,
                       'auxiliary_pools': auxiliary,
                       'fits_candidate': available >= minimum and all(p['fits_candidate'] for p in auxiliary),
                       'mapping_status': 'UNVERIFIED', 'mapping_limitations': option['mapping_limitations']})
    external = None
    if 'external_memory' in model:
        ddr = model['external_memory']
        efficiency = positive(ddr, 'efficiency')
        if efficiency > 1:
            raise ValueError('external memory efficiency must be <= 1')
        passes = num(ddr, 'traffic_passes', 2, integer=True)
        reserve = fraction(ddr, 'reserve_fraction')
        demand = peak_payload * metadata * passes / efficiency
        capacity = positive(ddr, 'bus_capacity_bps')
        required_bytes = math.ceil(sum(queue_bytes.values()) / (1 - reserve))
        auxiliary = auxiliary_pools(ddr)
        external = {'minimum_capacity_bytes': required_bytes,
                    'auxiliary_pools': auxiliary,
                    'fits_auxiliary_pools': all(p['fits_candidate'] for p in auxiliary),
                    'minimum_bus_capacity_bps': demand / (1 - reserve),
                    'fits_capacity': num(ddr, 'capacity_bytes', 1, integer=True) >= required_bytes,
                    'fits_bandwidth': capacity * (1 - reserve) >= demand,
                    'limitation': 'Payload passes plus declared metadata; controller granularity, refresh, ECC, bursts, arbitration and latency require measured validation.'}

    production = None
    if 'production' in model:
        p = model['production']
        availability = positive(p, 'availability')
        if availability > 1:
            raise ValueError('availability must be <= 1')
        cycle = positive(p, 'cycle_seconds')
        rate = positive(p, 'target_duts_per_hour')
        stations = math.ceil(rate * cycle / (3600 * availability))
        demand = stations * num(p, 'ports_per_station', 1, integer=True) + num(p, 'shared_golden_ports', integer=True)
        production = {'stations': stations, 'required_physical_ports': demand,
                      'capacity_duts_per_hour': stations * 3600 * availability / cycle,
                      'fits_declared_ports': len(ports) >= demand,
                      'scope': 'One DUT per station cycle; golden ports shared concurrently without contention as explicitly assumed. Does not solve scheduling.'}

    power = None
    if 'power' in model:
        p = model['power']
        total_input = total_heat = 0
        for rail in indexed(p.get('loads'), 'loads').values():
            efficiency = positive(rail, 'efficiency')
            if efficiency > 1:
                raise ValueError('power efficiency must be <= 1')
            output = num(rail, 'output_w') * num(rail, 'instances', 1, integer=True)
            incoming = output / efficiency
            outside = num(rail, 'fraction_heat_outside', 0, 1)
            total_input += incoming
            total_heat += incoming - output * outside
        rating = total_input / (1 - fraction(p, 'reserve_fraction'))
        chip_w = positive(p, 'fpga_dissipation_w')
        ambient = num(p, 'ambient_c', -273.15)
        target = num(p, 'target_junction_c', ambient)
        theta = positive(p, 'effective_theta_c_per_w')
        if chip_w > total_heat:
            raise ValueError('FPGA heat exceeds declared enclosure heat; power ledger inconsistent')
        power = {'input_w': total_input, 'enclosure_heat_w': total_heat,
                 'minimum_input_rating_w': rating,
                 'minimum_input_current_a': rating / positive(p, 'input_voltage_v'),
                 'predicted_junction_c': ambient + chip_w * theta,
                 'maximum_effective_theta_c_per_w': (target - ambient) / chip_w,
                 'fits_thermal_assumption': ambient + chip_w * theta <= target,
                 'limitation': 'Lumped assumed thermal path; not a power estimator or thermal qualification.'}
    blockers = []
    if not budget['fits_reserved_capacity']:
        blockers.append('traffic capacity fails')
    if not any(option['fits_candidate'] for option in memory):
        if not external or not (external['fits_capacity'] and external['fits_bandwidth'] and external['fits_auxiliary_pools']):
            blockers.append('no declared memory candidate meets capacity')
    if production and not production['fits_declared_ports']:
        blockers.append('insufficient physical ports for production')
    if power and not power['fits_thermal_assumption']:
        blockers.append('thermal assumption exceeds target')
    return {'status': 'CAPACITY_SHORTFALL' if blockers else 'ARITHMETIC_FEASIBLE',
            'blockers': blockers, 'channels_by_resource_type': channel_totals,
            'io_banks': io, 'logic': logic, 'buffer': {'hop': hid, 'owner': buffer['owner'],
            'bytes_by_physical_queue': queue_bytes, 'allocated_bytes': sum(queue_bytes.values()),
            'scope': 'Static per-port queues sized to each port maximum; maxima may occur in different scenarios.'},
            'memory_options': memory, 'external_memory': external, 'production': production, 'power': power,
            'evidence_scope': model['evidence_scope'],
            'limitations': 'Capacity envelope only. No part or speed-grade selection, bank placement, GT topology, IP license, synthesis, timing closure, memory mapping or hardware validation is performed.'}
