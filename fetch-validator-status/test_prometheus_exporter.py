import unittest
import json
from prometheus_exporter import PrometheusExporter

class TestPrometheusExporter(unittest.TestCase):

    def setUp(self):
        self.prom = PrometheusExporter(4711)
        # TODO: use relative path
        with open('/home/kwittek/development/sovrin/indy-node-monitor/fetch-validator-status/example_output.json') as json_file:
            self.prom.update(json.load(json_file))
        
    def test_uptime(self):
        uptime = self.prom.registry.get_sample_value('uptime', {'node': "Node1"})
        self.assertEqual(uptime, 576.0)

if __name__ == '__main__':
    unittest.main()
