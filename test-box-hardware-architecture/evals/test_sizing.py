"""Arithmetic and failure-path regression; no hardware or behavioral evaluation."""
import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('sizing', PACKAGE / 'scripts/sizing.py')
sizing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sizing)


def fixture(name):
    return json.loads((PACKAGE / 'examples' / name).read_text(encoding='utf-8'))


class SizingTests(unittest.TestCase):
    def setUp(self):
        self.traffic = fixture('traffic-camera-sized.json')
        self.resources = fixture('resource-camera.json')

    def test_heterogeneous_concurrency_and_per_hop(self):
        result = sizing.scenario_budget(self.traffic)
        stress = next(s for s in result['scenarios'] if s['scenario'] == 'STRESS')
        self.assertEqual(stress['payload_bps'], 6718464000)
        self.assertEqual(result['max_concurrent_ports'], 3)
        self.assertEqual(result['worst_by_hop']['CORE_AGG']['required_wire_bps'], 8817984000)
        self.assertEqual(result['worst_by_hop']['HOST_STORE']['minimum_payload_buffer_bytes'], 209952000)
        self.assertTrue(result['fits_reserved_capacity'])

    def test_continuous_bottlenecks_are_not_hidden_by_buffer(self):
        model = fixture('traffic-camera-proposed.json')
        result = sizing.scenario_budget(model)
        stress = next(s for s in result['scenarios'] if s['scenario'] == 'STRESS')
        self.assertEqual(stress['failing_hops'], ['CORE_AGG', 'HOST_STORE'])
        self.assertEqual(stress['bottleneck_hop'], 'CORE_AGG')
        self.assertTrue(result['worst_by_hop']['HOST_LINK']['fits_reserved_capacity'])

    def test_one_profile_per_physical_port(self):
        self.traffic['scenarios'][0]['active_streams'].append('D1-C')
        with self.assertRaisesRegex(ValueError, 'physical port'):
            sizing.scenario_budget(self.traffic)

    def test_missing_concurrency_rejected(self):
        self.traffic['scenarios'] = []
        with self.assertRaises(ValueError):
            sizing.scenario_budget(self.traffic)

    def test_discontinuous_and_missing_sink_rejected(self):
        for path in [['CORE_AGG', 'HOST_STORE'], ['INGRESS-D1']]:
            model = copy.deepcopy(self.traffic)
            model['streams'][0]['path'] = path
            with self.assertRaises(ValueError):
                sizing.scenario_budget(model)

    def test_disjoint_routes_have_different_worst_scenarios(self):
        model = dict(streams=[], hops=[], scenarios=[])
        for i in (1, 2):
            model['streams'].append(dict(id=f's{i}', port=f'p{i}', profile='x', width=1, height=1, fps=i, bits_per_pixel=8, path=[f'h{i}']))
            model['hops'].append(dict(id=f'h{i}', **{'from':f'p{i}', 'to':'sink'}, capacity_bps=100, packet_factor=1, coding_efficiency=1, reserve_fraction=0, stall_seconds=0, buffer_owner='host', capacity_basis='synthetic'))
            model['scenarios'].append(dict(id=f'c{i}', active_streams=[f's{i}'], required_sink='sink', rationale='mutually exclusive'))
        result = sizing.scenario_budget(model)
        self.assertEqual(result['max_concurrent_ports'], 1)
        self.assertEqual(result['physical_ports'], ['p1','p2'])
        self.assertEqual(result['worst_by_hop']['h1']['scenario'], 'c1')
        self.assertEqual(result['worst_by_hop']['h2']['scenario'], 'c2')

    def test_reference_and_numeric_errors(self):
        for field, value in [('capacity_bps',0), ('packet_factor',.9), ('coding_efficiency',0), ('reserve_fraction',1), ('stall_seconds',-1), ('capacity_bps',True), ('capacity_bps',float('nan'))]:
            model = copy.deepcopy(self.traffic)
            model['hops'][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                sizing.scenario_budget(model)
        self.traffic['scenarios'][0]['active_streams'] = ['absent']
        with self.assertRaises(ValueError):
            sizing.scenario_budget(self.traffic)

    def test_resource_channel_bank_logic_and_production(self):
        result = sizing.resource(self.resources, self.traffic)
        self.assertEqual(result['channels_by_resource_type'], {'GT':16})
        self.assertEqual([x['minimum_banks'] for x in result['io_banks']], [3,1])
        self.assertEqual(result['logic']['lut']['minimum_device_capacity'], 51429)
        self.assertEqual(result['production']['stations'], 2)
        self.assertEqual(result['production']['required_physical_ports'], 3)

    def test_memory_rounds_each_queue_and_checks_auxiliary_pool(self):
        result = sizing.resource(self.resources, self.traffic)
        self.assertEqual(result['buffer']['allocated_bytes'], 1876224)
        bram, uram = result['memory_options']
        self.assertEqual(bram['blocks_by_queue'], {'D1':221, 'D2':221, 'GOLDEN':69})
        self.assertEqual(bram['minimum_device_blocks'], 822)
        self.assertFalse(bram['fits_candidate'])
        self.assertEqual(uram['minimum_device_blocks'], 93)
        self.assertTrue(uram['fits_candidate'])
        self.resources['memory_options'][1]['auxiliary_pools'][0]['available_blocks'] = 1
        self.assertFalse(sizing.resource(self.resources, self.traffic)['memory_options'][1]['fits_candidate'])

    def test_ddr_checks_read_write_bandwidth_not_only_capacity(self):
        self.resources['memory_options'] = self.resources['memory_options'][:1]
        self.resources['external_memory']['bus_capacity_bps'] = 1e9
        result = sizing.resource(self.resources, self.traffic)
        self.assertTrue(result['external_memory']['fits_capacity'])
        self.assertFalse(result['external_memory']['fits_bandwidth'])
        self.assertEqual(result['status'], 'CAPACITY_SHORTFALL')

    def test_physical_channels_are_not_just_active_channels(self):
        self.resources['ports'][0]['resource_type'] = 'DPHY_IO'
        result = sizing.resource(self.resources, self.traffic)
        self.assertEqual(result['channels_by_resource_type'], {'DPHY_IO':4, 'GT':12})

    def test_buffer_owner_and_port_coverage(self):
        self.resources['buffer']['owner'] = 'HOST_RAM'
        with self.assertRaisesRegex(ValueError, 'owner'):
            sizing.resource(self.resources, self.traffic)
        self.resources['buffer']['owner'] = 'FPGA'
        self.resources['ports'].pop()
        with self.assertRaisesRegex(ValueError, 'ports'):
            sizing.resource(self.resources, self.traffic)

    def test_external_load_heat_and_thermal_failure(self):
        result = sizing.resource(self.resources, self.traffic)
        self.assertAlmostEqual(result['power']['input_w'], 53.45751633986928)
        self.assertAlmostEqual(result['power']['enclosure_heat_w'], 29.45751633986928)
        self.assertEqual(result['power']['predicted_junction_c'], 75)
        self.resources['power']['effective_theta_c_per_w'] = 4
        self.assertEqual(sizing.resource(self.resources, self.traffic)['status'], 'CAPACITY_SHORTFALL')

    def test_invalid_intervals(self):
        self.resources['functions'][0]['lut'] = [100, 1]
        with self.assertRaises(ValueError):
            sizing.resource(self.resources, self.traffic)

    def test_missing_and_malformed_resource_objects(self):
        for key, value in [('memory_options', []), ('buffer', []), ('power', []), ('external_memory', []), ('additional_channels', ['invalid'])]:
            model = copy.deepcopy(self.resources)
            model[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                sizing.resource(model, self.traffic)

    def test_resource_cli_exits(self):
        script = PACKAGE / 'scripts/arch_tools.py'
        for filename, expected in [('traffic-camera-proposed.json',1), ('traffic-camera-sized.json',0)]:
            run = subprocess.run([sys.executable, '-X', 'utf8', str(script), 'resource', str(PACKAGE/'examples/resource-camera.json'), '--traffic', str(PACKAGE/'examples'/filename)], capture_output=True, encoding='utf-8')
            self.assertEqual(run.returncode, expected, run.stdout + run.stderr)
            self.assertIn('evidence_scope', json.loads(run.stdout))


if __name__ == '__main__':
    unittest.main()
