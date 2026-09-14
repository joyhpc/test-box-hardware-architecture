#!/usr/bin/env python3
"""Offline architecture analysis. No hardware, network, or third-party packages."""
import argparse
import json
import math
import re
import importlib.util
from collections import deque
from pathlib import Path

FIELDS = ('power', 'clock', 'reset', 'enable', 'gpio', 'receiver', 'transmitter',
          'termination', 'bias', 'pulls', 'ownership', 'firmware', 'communication',
          'protection', 'back_power_risk', 'evidence')
STAGES = ('requirement', 'function', 'module', 'interface', 'implementation', 'validation')
_spec = importlib.util.spec_from_file_location('test_box_sizing', Path(__file__).with_name('sizing.py'))
sizing = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sizing)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON key: {key}')
        result[key] = value
    return result


def read_json(path):
    def invalid_constant(value):
        raise ValueError(f'non-finite JSON number: {value}')
    return json.loads(Path(path).read_text(encoding='utf-8-sig'),
                      object_pairs_hook=unique_object, parse_constant=invalid_constant)


def unknown(value):
    if value is None:
        return True
    if isinstance(value, str):
        value = value.strip().upper()
        return not value or value == 'N/A' or bool(re.search(r'(?<![A-Z])(?:UNKNOWN|TBD)(?![A-Z])', value))
    if isinstance(value, dict):
        return not value or any(unknown(v) for v in value.values())
    if isinstance(value, list):
        return not value or any(unknown(v) for v in value)
    return False


def state_diff(model, before, after):
    states = model.get('states')
    if not isinstance(states, dict) or before not in states or after not in states:
        raise ValueError('states must contain both named states')
    left, right = states[before], states[after]
    if not isinstance(left, dict) or not isinstance(right, dict) or not left or not right:
        raise ValueError('each state must contain at least one module')
    rows, gaps = [], []
    for module in sorted(set(left) | set(right)):
        a, b = left.get(module, {}), right.get(module, {})
        if not isinstance(a, dict) or not isinstance(b, dict):
            raise ValueError(f'{module}: module state must be an object')
        for field in sorted(set(FIELDS) | set(a) | set(b)):
            missing = field not in a or field not in b
            av, bv = a.get(field), b.get(field)
            unresolved = missing or unknown(av) or unknown(bv)
            changed = av != bv or missing
            if unresolved:
                gaps.append({'module': module, 'field': field,
                             'before_missing': field not in a, 'after_missing': field not in b})
            if changed or unresolved:
                rows.append({'module': module, 'field': field, 'before_value': av, 'after_value': bv,
                             'changed': changed, 'unresolved': unresolved})
    return {'before': before, 'after': after, 'differences': rows, 'gaps': gaps,
            'status': 'INCOMPLETE' if gaps else 'STRUCTURALLY_COMPLETE',
            'engineering_review': 'Check unchanged hazards and transition windows; no safety verdict.'}


def graph(model):
    raw_nodes, edges = model.get('nodes'), model.get('edges')
    if not isinstance(raw_nodes, list) or not raw_nodes or not isinstance(edges, list):
        raise ValueError('nonempty nodes list and edges list required')
    nodes = {}
    for node in raw_nodes:
        if not isinstance(node, dict) or not isinstance(node.get('id'), str) or not node['id'].strip():
            raise ValueError('each node needs a nonempty string id')
        if node['id'] in nodes:
            raise ValueError(f'duplicate node: {node["id"]}')
        nodes[node['id']] = node
    adjacency = {key: set() for key in nodes}
    for edge in edges:
        if not isinstance(edge, dict) or edge.get('from') not in nodes or edge.get('to') not in nodes:
            raise ValueError(f'dangling or malformed edge: {edge}')
        adjacency[edge['from']].add(edge['to'])
    return nodes, adjacency


def dependency(model, changed=None):
    nodes, adj = graph(model)
    indegree = {key: 0 for key in nodes}
    for targets in adj.values():
        for target in targets:
            indegree[target] += 1
    queue = deque(sorted(key for key, degree in indegree.items() if degree == 0))
    order = []
    while queue:
        key = queue.popleft()
        order.append(key)
        for target in sorted(adj[key]):
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    # Reachability identifies actual cycle participants; blocked descendants are separate.
    def reachable(start):
        seen, pending = set(), list(adj[start])
        while pending:
            key = pending.pop()
            if key not in seen:
                seen.add(key)
                pending.extend(adj[key] - seen)
        return seen
    cyclic = sorted(key for key in nodes if key in reachable(key))
    blocked = sorted(set(nodes) - set(order) - set(cyclic))
    impact = None
    if changed is not None:
        if changed not in nodes:
            raise ValueError(f'unknown changed node: {changed}')
        impact = sorted(reachable(changed) - {changed})
    return {'status': 'CYCLE' if cyclic else 'ACYCLIC', 'order': order,
            'cycle_nodes': cyclic, 'blocked_descendants': blocked,
            'possibly_affected': impact,
            'scope': 'Edges mean prerequisite -> dependent. Reachability is review scope, not redesign proof.'}


def number(model, key, minimum=0, maximum=None, integer=False):
    value = model.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{key}: finite numeric value required')
    if value < minimum or (maximum is not None and value > maximum):
        raise ValueError(f'{key}: value outside allowed range')
    if integer and int(value) != value:
        raise ValueError(f'{key}: integer required')
    return value


def budget(model):
    if isinstance(model.get('streams'), list):
        return sizing.scenario_budget(model)
    width = number(model, 'width', 1, integer=True)
    height = number(model, 'height', 1, integer=True)
    fps = number(model, 'fps', 0)
    bpp = number(model, 'bits_per_pixel', 0)
    streams = number(model, 'streams', 1, integer=True)
    factor = number(model, 'packet_factor', 1)
    efficiency = number(model, 'coding_efficiency', 0, 1)
    capacity = number(model, 'wire_capacity_bps', 0)
    reserve = number(model, 'reserve_fraction', 0, 1)
    stall = number(model, 'stall_seconds', 0)
    if min(fps, bpp, efficiency, capacity) <= 0 or reserve >= 1:
        raise ValueError('fps/bpp/efficiency/capacity must be positive; reserve < 1')
    payload = width * height * fps * bpp * streams
    required = payload * factor / efficiency
    buffer_bytes = payload * stall / 8
    if not all(math.isfinite(x) for x in (payload, required, buffer_bytes)):
        raise ValueError('calculation overflow')
    return {'payload_bps': payload, 'required_wire_bps': required,
            'wire_capacity_bps': capacity, 'headroom_fraction': 1 - required / capacity,
            'fits_reserved_capacity': required <= capacity * (1 - reserve),
            'minimum_payload_buffer_bytes_for_zero_service_stall': math.ceil(buffer_bytes),
            'limitations': 'Active pixels only; no implicit blanking/compression. Stall buffer excludes burst, metadata and margin. Verify each hop.'}


def trace(model):
    nodes, adj = graph(model)
    issues = []
    for key, node in nodes.items():
        if node.get('kind') not in STAGES:
            issues.append(f'{key}: invalid kind')
    if issues:
        return {'status': 'INCOMPLETE', 'issues': issues}
    incoming = {key: set() for key in nodes}
    for source, targets in adj.items():
        for target in targets:
            incoming[target].add(source)
            if STAGES.index(nodes[target]['kind']) != STAGES.index(nodes[source]['kind']) + 1:
                issues.append(f'{source}->{target}: skipped or reversed trace stage')
    for stage in STAGES:
        if not any(n['kind'] == stage for n in nodes.values()):
            issues.append(f'missing stage: {stage}')
    for key, node in nodes.items():
        if node['kind'] != 'requirement' and not incoming[key]:
            issues.append(f'{key}: orphan without upstream reason')
        if node['kind'] != 'validation' and not adj[key]:
            issues.append(f'{key}: missing downstream trace')
        if node['kind'] == 'validation':
            for field in ('pass_criteria', 'method'):
                if unknown(node.get(field)):
                    issues.append(f'{key}: missing {field}')
            status = node.get('status')
            if status not in ('PLANNED', 'PASS', 'FAIL', 'UNKNOWN'):
                issues.append(f'{key}: invalid validation status')
            if status in ('PASS', 'FAIL') and unknown(node.get('evidence')):
                issues.append(f'{key}: {status} needs evidence')
    return {'status': 'INCOMPLETE' if issues else 'STRUCTURALLY_COMPLETE', 'issues': issues,
            'limitation': 'Checks references and closure shape, not requirement quality or evidence truth.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('diff', 'dependency', 'budget', 'resource', 'trace'):
        child = sub.add_parser(command)
        child.add_argument('input', type=Path)
        child.add_argument('--output', type=Path)
        if command == 'diff':
            child.add_argument('--before', required=True)
            child.add_argument('--after', required=True)
        if command == 'dependency':
            child.add_argument('--changed')
        if command == 'resource':
            child.add_argument('--traffic', required=True, type=Path)
    args = parser.parse_args()
    try:
        model = read_json(args.input)
        if not isinstance(model, dict):
            raise ValueError('top-level JSON must be an object')
        if args.command == 'diff':
            result = state_diff(model, args.before, args.after)
        elif args.command == 'dependency':
            result = dependency(model, args.changed)
        elif args.command == 'budget':
            result = budget(model)
        elif args.command == 'resource':
            result = sizing.resource(model, read_json(args.traffic))
        else:
            result = trace(model)
        output = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
        if args.output:
            if args.output.resolve() == args.input.resolve():
                raise ValueError('output must not overwrite input')
            if args.output.exists():
                raise ValueError('output already exists; choose a new report path')
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output, encoding='utf-8')
        else:
            print(output, end='')
        failed = result.get('status') in ('INCOMPLETE', 'CYCLE', 'CAPACITY_SHORTFALL') or result.get('fits_reserved_capacity') is False
        return 1 if failed else 0
    except (ValueError, OSError, TypeError, OverflowError) as exc:
        print(json.dumps({'status': 'INPUT_ERROR', 'error': str(exc)}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
