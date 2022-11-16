import plugin_collection
import argparse
import json

class main(plugin_collection.Plugin):
    
    def __init__(self):
        super().__init__()
        self.index = 1
        self.name = 'Alerts'
        self.description = ''
        self.type = ''

    # def description(self)
    #     return self.description

    def parse_args(self, parser):
        parser.add_argument("--alerts", action="store_true", help="Alert Plug-in: Filter results based on alerts.  Only return data for nodes containing detected 'info', 'warnings', or 'errors'.")

    def load_parse_args(self, args):
        global verbose
        verbose = args.verbose

        self.enabled = args.alerts

    async def perform_operation(self, result, network_name, response, verifiers):
        # Filter on alerts
        filtered_result = []
        for item in result:
            if ("info" in item["status"] and item["status"]["info"] > 0) \
                or ("warnings" in item["status"] and item["status"]["warnings"] > 0) \
                or ("errors" in item["status"] and item["status"]["errors"] > 0):
                filtered_result.append(item)
        result = filtered_result
        return result

