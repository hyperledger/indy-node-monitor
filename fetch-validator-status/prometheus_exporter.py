from prometheus_client import start_http_server
from prometheus_client import CollectorRegistry, Gauge

class PrometheusExporter():
    def __init__(self, port):
        self.port = port
        self.registry = CollectorRegistry()
        self.g_uptime = Gauge('uptime', 'Uptime of node in seconds', ['node'], registry=self.registry)

    def start(self):
        start_http_server(self.port)

    def update(self, metrics):
        for node_name, data in metrics.items():
            self._update_metrics_for_node(data)

    def _update_metrics_for_node(self, node):
        node_info = node['result']['data']['Node_info']
        name = node_info['Name']

        uptime = node_info['Metrics']['uptime']
        self.g_uptime.labels(name).set(uptime)


