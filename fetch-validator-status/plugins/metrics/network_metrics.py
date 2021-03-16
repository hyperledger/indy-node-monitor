import plugin_collection
from .google_sheets import gspread_authZ, gspread_append_sheet
import datetime
import argparse
import os

class main(plugin_collection.Plugin):
    
    def __init__(self):
        super().__init__()
        self.index = 4
        self.name = 'Network Metrics'
        self.description = ''
        self.type = ''
        self.gauth_json = None
        self.file_name = None
        self.worksheet_name = None


    def parse_args(self, parser):
        parser.add_argument("--mlog", action="store_true", help="Network Metrics Plug-in: Metrics log argument uses google sheets api and requires, Google API Credentials json file name (file must be in root folder), google sheet file name and worksheet name. ex: --mlog --json [Json File Name] --file [Google Sheet File Name] --worksheet [Worksheet name]")
        parser.add_argument("--json", default=os.environ.get('JSON') , help="Google API Credentials json file name (file must be in root folder). Can be specified using the 'JSON' environment variable.", nargs='*')
        parser.add_argument("--file", default=os.environ.get('FILE') , help="Specify which google sheets file you want to log too. Can be specified using the 'FILE' environment variable.", nargs='*')
        parser.add_argument("--worksheet", default=os.environ.get('WORKSHEET') , help="Specify which worksheet you want to log too. Can be specified using the 'WORKSHEET' environment variable.", nargs='*')

    def load_parse_args(self, args):
        global verbose
        verbose = args.verbose
        # Support names and paths containing spaces.
        # Other workarounds including the standard of putting '"'s around values containing spaces does not always work.
        if args.json:
            args.json = ' '.join(args.json)
        if args.file:
            args.file = ' '.join(args.file)
        if args.worksheet:
            args.worksheet = ' '.join(args.worksheet)

        if args.mlog:
            if args.json and args.file and args.worksheet:
                self.enabled = args.mlog
                self.gauth_json = args.json
                self.file_name = args.file
                self.worksheet_name = args.worksheet
            else:
                print('Metrics log argument uses google sheets api and requires, Google API Credentials json file name (file must be in root folder), google sheet file name and worksheet name.')
                print('ex: --mlog --json [Json File Name] --file [Google Sheet File Name] --worksheet [Worksheet name]')
                exit()

    async def perform_operation(self, result, network_name, response, verifiers):

        authD_client = gspread_authZ(self.gauth_json)
        message = ""
        num_of_nodes = 0
        nodes_offline = 0
        time = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S') # formated to 12/3/2020 21:27:49

        for node in result:
            num_of_nodes += 1
            if node["status"]["ok"] == False:
                nodes_offline += 1

        networkResilience = num_of_nodes - round((num_of_nodes - 1 ) / 3)

        # Could have a stepped warning system
        if nodes_offline >= networkResilience:
            message = "Network Resilience Danger!"

        active_nodes = num_of_nodes - nodes_offline

        row = [time, network_name, num_of_nodes, nodes_offline, networkResilience, active_nodes, message]
        print(row)
        gspread_append_sheet(authD_client, self.file_name, self.worksheet_name, row)
        print(f"\033[92mPosted to {self.file_name} in sheet {self.worksheet_name}.\033[m")
        return result