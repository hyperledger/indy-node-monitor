from prometheus_client import start_http_server
from prometheus_client import CollectorRegistry, Gauge

class PrometheusExporter():
    def __init__(self, port):
        self.port = port
        self.registry = CollectorRegistry()
        self.g = Gauge('node_count', 'Number of active codes', registry=self.registry)

    def start(self):
        start_http_server(self.port)

    def update(self, metrics):
        self.g.set(len(metrics.keys()))
