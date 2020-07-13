import unittest
import json
from prometheus_exporter import PrometheusExporter

class TestPrometheusExporter(unittest.TestCase):

    def setUp(self):
        self.prom = PrometheusExporter(4711)
        # TODO: use relative path
        with open('/home/kwittek/development/sovrin/indy-node-monitor/fetch-validator-status/example_output.json') as json_file:
            self.prom.update(json.load(json_file))
        
    def test_node_count(self):
        node_count = self.prom.registry.get_sample_value('node_count')
        self.assertEqual(node_count, 4.0)

if __name__ == '__main__':
    unittest.main()
