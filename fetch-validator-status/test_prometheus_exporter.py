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
        uptime = self.prom.registry.get_sample_value('uptime', {'node': 'Node1'})
        self.assertEqual(uptime, 576.0)

    def test_transaction_ledger_count(self):
        ledger = self.prom.registry.get_sample_value('transaction_count', {'node': 'Node1', 'ledger': 'ledger'})
        self.assertEqual(ledger, 5)
    
    def test_transaction_pool_count(self):
        pool = self.prom.registry.get_sample_value('transaction_count', {'node':'Node1', 'ledger':'pool'})
        self.assertEqual(pool, 4)

    def test_transaction_config_count(self):
        config = self.prom.registry.get_sample_value('transaction_count', {'node':'Node1','ledger':'config'})
        self.assertEqual(config, 0)

    def test_transaction_audit_count(self):
        audit = self.prom.registry.get_sample_value('transaction_count', {'node':'Node1','ledger':'audit'})
        self.assertEqual(audit, 3)

    def test_read_transactions(self):
        read_transaction = self.prom.registry.get_sample_value('transaction_rate', {'node': 'Node1', 'mode': 'read'})
        self.assertEqual(read_transaction, 0.0606915686)

    def test_write_transactions(self):
        write_transaction = self.prom.registry.get_sample_value('transaction_rate', {'node': 'Node1', 'mode': 'write'})
        self.assertEqual(write_transaction, 0.0)

    def test_master_throughput(self):
        master_throughput = self.prom.registry.get_sample_value('throughput', {'node': 'Node1'})
        self.assertEqual(master_throughput, 42.7)
        
if __name__ == '__main__':
    unittest.main()
