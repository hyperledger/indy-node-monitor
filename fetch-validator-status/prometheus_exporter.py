from prometheus_client import start_http_server
from prometheus_client import CollectorRegistry, Gauge


class PrometheusExporter():
    def __init__(self, port):
        self.port = port
        self.registry = CollectorRegistry()
        self.g_uptime = Gauge('uptime', 'Uptime of node in seconds',
                              ['node'], registry=self.registry)
        self.g_transaction_count = Gauge('transaction_count',
                                         'Number of transactions in each ledger',
                                         ['node', 'ledger'], registry=self.registry)
        self.g_transaction_rate = Gauge('transaction_rate',
                                        'Rate of transactions in seconds',
                                        ['node', 'mode'], registry=self.registry)

    def start(self):
        start_http_server(self.port, registry=self.registry)

    def update(self, metrics):
        for node_name, data in metrics.items():
            self._update_metrics_for_node(data)

    def _update_metrics_for_node(self, node):
        node_info = node['result']['data']['Node_info']
        name = node_info['Name']

        uptime = node_info['Metrics']['uptime']
        self.g_uptime.labels(name).set(uptime)

        transaction_count = node_info['Metrics']['transaction-count']
        self.g_transaction_count.labels(name, 'ledger').set(transaction_count['ledger'])
        self.g_transaction_count.labels(name, 'pool').set(transaction_count['pool'])
        self.g_transaction_count.labels(name, 'config').set(transaction_count['config'])
        self.g_transaction_count.labels(name, 'audit').set(transaction_count['audit'])

        transaction_rate_avg = node_info['Metrics']['average-per-second']
        self.g_transaction_rate.labels(name, 'read').set(transaction_rate_avg['read-transactions'])
        self.g_transaction_rate.labels(name, 'write').set(transaction_rate_avg['write-transactions'])
