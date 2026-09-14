import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('arch_tools', ROOT / 'scripts/arch_tools.py')
T = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(T)


class ArchitectureToolsTests(unittest.TestCase):
    def states(self):
        return {'states': {'A': {'M': {k: 'defined' for k in T.FIELDS}},
                           'B': {'M': {k: 'defined' for k in T.FIELDS}}}}

    def test_unchanged_unknown_is_visible(self):
        model = self.states()
        model['states']['A']['M']['receiver'] = 'UNKNOWN'
        model['states']['B']['M']['receiver'] = 'UNKNOWN'
        result = T.state_diff(model, 'A', 'B')
        self.assertEqual(result['status'], 'INCOMPLETE')
        self.assertFalse(result['differences'][0]['changed'])

    def test_removed_module_and_missing_fields(self):
        model = self.states()
        model['states']['A']['OLD'] = {'power': 'ON'}
        del model['states']['B']['M']['reset']
        result = T.state_diff(model, 'A', 'B')
        self.assertTrue(any(g['module'] == 'OLD' and g['after_missing'] for g in result['gaps']))
        self.assertTrue(any(g['field'] == 'reset' and g['after_missing'] for g in result['gaps']))

    def test_complete_is_not_safety_pass(self):
        result = T.state_diff(self.states(), 'A', 'B')
        self.assertEqual(result['status'], 'STRUCTURALLY_COMPLETE')
        self.assertEqual(result['differences'], [])
        self.assertIn('no safety verdict', result['engineering_review'])

    def test_missing_state_is_error(self):
        with self.assertRaises(ValueError):
            T.state_diff(self.states(), 'A', 'MISSING')

    def test_nested_unknown(self):
        self.assertTrue(T.unknown({'value': {'voltage': None}}))
        self.assertFalse(T.unknown({'asserted': False, 'level': 0}))

    def test_unknown_embedded_in_description_and_bare_na(self):
        self.assertTrue(T.unknown('DUT asserted; pin injection UNKNOWN'))
        self.assertTrue(T.unknown('N/A'))
        self.assertFalse(T.unknown('N/A: passive fixture has no firmware'))

    def test_state_labels_do_not_overwrite_row_metadata(self):
        model = self.states()
        model['states']['module'] = model['states'].pop('A')
        model['states']['field'] = model['states'].pop('B')
        model['states']['module']['M']['power'] = 'OFF'
        result = T.state_diff(model, 'module', 'field')
        row = result['differences'][0]
        self.assertEqual(row['module'], 'M')
        self.assertEqual(row['field'], 'power')
        self.assertEqual(row['before_value'], 'OFF')

    def test_dependency_cycle_separates_downstream(self):
        model = {'nodes': [{'id': x} for x in 'ABCD'],
                 'edges': [{'from': 'A', 'to': 'B'}, {'from': 'B', 'to': 'A'},
                           {'from': 'B', 'to': 'C'}]}
        result = T.dependency(model, 'A')
        self.assertEqual(result['cycle_nodes'], ['A', 'B'])
        self.assertEqual(result['blocked_descendants'], ['C'])
        self.assertEqual(result['order'], ['D'])
        self.assertEqual(result['possibly_affected'], ['B', 'C'])

    def test_dependency_self_cycle(self):
        result = T.dependency({'nodes': [{'id': 'A'}], 'edges': [{'from': 'A', 'to': 'A'}]})
        self.assertEqual(result['cycle_nodes'], ['A'])

    def test_duplicate_and_dangling_nodes(self):
        for model in ({'nodes': [{'id': 'A'}, {'id': 'A'}], 'edges': []},
                      {'nodes': [{'id': 'A'}], 'edges': [{'from': 'A', 'to': 'B'}]}):
            with self.assertRaises(ValueError):
                T.dependency(model)

    def test_budget_units_and_reserve(self):
        model = T.read_json(ROOT / 'examples/budget-demo.json')
        result = T.budget(model)
        self.assertEqual(result['payload_bps'], 5971968000)
        self.assertAlmostEqual(result['required_wire_bps'], 7838208000)
        self.assertFalse(result['fits_reserved_capacity'])
        self.assertEqual(result['minimum_payload_buffer_bytes_for_zero_service_stall'], 1492992)
        model['reserve_fraction'] = 0
        self.assertTrue(T.budget(model)['fits_reserved_capacity'])

    def test_invalid_budget_inputs(self):
        model = T.read_json(ROOT / 'examples/budget-demo.json')
        for field, value in [('streams', 1.2), ('fps', True), ('fps', 0),
                             ('coding_efficiency', 0), ('packet_factor', 0.9),
                             ('stall_seconds', -1), ('wire_capacity_bps', float('inf')),
                             ('reserve_fraction', 1)]:
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                T.budget(dict(model, **{field: value}))

    def test_trace_unknown_acceptance_cannot_close(self):
        model = T.read_json(ROOT / 'examples/trace-demo.json')
        self.assertEqual(T.trace(model)['status'], 'INCOMPLETE')
        model['nodes'][-1]['pass_criteria'] = 'Synthetic: Core 3.0–3.6V, no reset, fault record present'
        self.assertEqual(T.trace(model)['status'], 'STRUCTURALLY_COMPLETE')
        model['nodes'][-1]['status'] = 'PASS'
        self.assertEqual(T.trace(model)['status'], 'INCOMPLETE')

    def test_trace_orphan_and_stage_skip(self):
        model = T.read_json(ROOT / 'examples/trace-demo.json')
        model['nodes'].append({'id': 'ORPHAN', 'kind': 'module'})
        model['edges'].append({'from': 'REQ-01', 'to': 'VAL-01'})
        issues = T.trace(model)['issues']
        self.assertTrue(any('ORPHAN' in x for x in issues))
        self.assertTrue(any('skipped' in x for x in issues))

    def test_duplicate_json_and_nonfinite_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'bad.json'
            for data in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}'):
                path.write_text(data)
                with self.assertRaises(ValueError):
                    T.read_json(path)

    def test_cli_does_not_overwrite_input_or_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'input.json'
            original = (ROOT / 'examples/budget-demo.json').read_text()
            path.write_text(original)
            for output in (path, Path(directory) / 'existing.json'):
                if output != path:
                    output.write_text('keep me')
                result = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'scripts/arch_tools.py'),
                                         'budget', str(path), '--output', str(output)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(path.read_text(), original)
                if output != path:
                    self.assertEqual(output.read_text(), 'keep me')

    def test_cli_examples_emit_parseable_results_and_exit_codes(self):
        for args, expected in [(['diff', 'lifecycle-demo.json', '--before', 'DUT_OFF', '--after', 'ACTIVE'], 1),
                               (['dependency', 'dependency-demo.json', '--changed', 'SERDES'], 0),
                               (['budget', 'budget-demo.json'], 1), (['trace', 'trace-demo.json'], 1)]:
            args[1] = str(ROOT / 'examples' / args[1])
            result = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'scripts/arch_tools.py'), *args],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
            self.assertIsInstance(json.loads(result.stdout), dict)


if __name__ == '__main__':
    unittest.main()
