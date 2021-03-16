import plugin_collection
import json

class main(plugin_collection.Plugin):
    
    def __init__(self):
        super().__init__()
        self.index = 2
        self.name = 'Status Only'
        self.description = ''
        self.type = ''

    def parse_args(self, parser):
        parser.add_argument("--status", action="store_true", help="Status Only Plug-in: Get status only.  Suppresses detailed results.")

    def load_parse_args(self, args):
        global verbose
        verbose = args.verbose
        
        self.enabled = args.status
    
    async def perform_operation(self, result, network_name, response, verifiers):
        for node in result:
            if "response" in node:
                node.pop("response")
        return result
