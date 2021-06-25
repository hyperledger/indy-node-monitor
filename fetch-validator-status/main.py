import argparse
import asyncio
import json
import os
import indy_vdr
from util import (
    enable_verbose,
    log,
    create_did
)
from fetch_status import FetchStatus
from pool import PoolCollection
from pool import Networks
from plugin_collection import PluginCollection

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch the status of all the indy-nodes within a given pool.")
    parser.add_argument("--net", choices=Networks.get_ids(), help="Connect to a known network using an ID.")
    parser.add_argument("--list-nets", action="store_true", help="List known networks.")
    parser.add_argument("--genesis-url", default=os.environ.get('GENESIS_URL') , help="The url to the genesis file describing the ledger pool.  Can be specified using the 'GENESIS_URL' environment variable.")
    parser.add_argument("--genesis-path", default=os.getenv("GENESIS_PATH"), help="The path to the genesis file describing the ledger pool.  Can be specified using the 'GENESIS_PATH' environment variable.")
    parser.add_argument("-s", "--seed", default=os.environ.get('SEED') , help="The privileged DID seed to use for the ledger requests.  Can be specified using the 'SEED' environment variable. If DID seed is not given the request will run anonymously.")
    parser.add_argument("--nodes", help="The comma delimited list of the nodes from which to collect the status.  The default is all of the nodes in the pool.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    parser.add_argument("--web", action="store_true", help="Start API server.")

    monitor_plugins = PluginCollection('plugins')
    monitor_plugins.get_parse_args(parser)
    args, unknown = parser.parse_known_args()
    monitor_plugins.load_all_parse_args(args)

    if args.web:
        log("Starting web server ...")
        # Pass verbose to rest api through env var
        os.environ['VERBOSE'] = str(args.verbose)
        os.system('uvicorn rest_api:app --reload --host 0.0.0.0 --port 8080')
    else:
        log("Starting from the command line ...")
        enable_verbose(args.verbose)

        if args.list_nets:
            print(json.dumps(Networks.get_networks(), indent=2))
            exit()

        log("indy-vdr version:", indy_vdr.version())
        did_seed = None if not args.seed else args.seed
        ident = create_did(did_seed)
        networks = Networks()
        pool_collection = PoolCollection(args.verbose, networks)
        network = networks.resolve(args.net, args.genesis_url, args.genesis_path)
        node_info = FetchStatus(args.verbose, pool_collection)
        result = asyncio.get_event_loop().run_until_complete(node_info.fetch(network.id, monitor_plugins, args.nodes, ident))
        print(json.dumps(result, indent=2))