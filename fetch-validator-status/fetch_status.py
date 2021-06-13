import argparse
import asyncio
import json
import os
import sys

import indy_vdr
from fetch_status_library import (
    enable_verbose,
    log,
    fetch_status,
    load_network_list,
    list_networks,
    init_network_args,
    create_did
)
from DidKey import DidKey

from plugin_collection import PluginCollection

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch the status of all the indy-nodes within a given pool.")
    parser.add_argument("--net", choices=list_networks(), help="Connect to a known network using an ID.")
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
            print(json.dumps(load_network_list(), indent=2))
            exit()

        log("indy-vdr version:", indy_vdr.version())

        did_seed = None if not args.seed else args.seed    
        ident = create_did(did_seed)

        network_info = init_network_args(network=args.net, genesis_url=args.genesis_url, genesis_path=args.genesis_path)
        result = asyncio.get_event_loop().run_until_complete(fetch_status(monitor_plugins, network_info.genesis_path, args.nodes, ident, network_info.network_name))
        print(json.dumps(result, indent=2))