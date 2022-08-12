import plugin_collection
from datetime import datetime, timezone
from datetime import timedelta

class main(plugin_collection.Plugin):

    def __init__(self):
        super().__init__()
        self.index = 1
        self.name = 'Generate Network Upgrade Schedule'
        self.description = 'Generates a network upgrade schedule for a given network.'
        self.type = ''

    def parse_args(self, parser):
        parser.add_argument("--upgrade-schedule", action="store_true", help="Enables the Generate Network Upgrade Schedule plugin.")
        parser.add_argument("--upgrade-start", default=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z'), help="The start date and time for the upgrade schedule, in the form yyyy-mm-ddTHH:MM:SSz; for example 2022-08-13T05:00:00-0700 to schedule the first upgrade for August 13, 2022 @ 05:00 PDT (12:00 UTC)")
        parser.add_argument("--upgrade-interval", default=5, help="The time interval in minutes between node upgrades.  Defaults to 5 minutes.")

    def load_parse_args(self, args):
        global verbose
        verbose = args.verbose

        self.enabled = args.upgrade_schedule
        self.start_date_time = datetime.strptime(args.upgrade_start, '%Y-%m-%dT%H:%M:%S%z')
        self.interval = int(args.upgrade_interval)

    async def perform_operation(self, result, network_name, response, verifiers):
        filtered_result = {}
        counter = 0
        for item in result:
            if "Node_info" in item["response"]["result"]["data"]:
                schedule = self.start_date_time + timedelta(minutes = (self.interval * counter))
                filtered_result[item["response"]["result"]["data"]["Node_info"]["did"]] = schedule.strftime('%Y-%m-%dT%H:%M:%S%z')
            counter += 1
        result = filtered_result
        return result