import json
import os
import sys

import urllib.request
from indy_vdr.ledger import (
    build_get_validator_info_request,
    build_get_txn_request,
)
from indy_vdr.pool import open_pool
from DidKey import DidKey

from plugin_collection import PluginCollection

verbose = False

def enable_verbose(enable):
    global verbose
    verbose = enable

def log(*args):
    if verbose:
        print(*args, "\n", file=sys.stderr)

async def fetch_status(monitor_plugins: PluginCollection, genesis_path: str, nodes: str = None, ident: DidKey = None, network_name: str = None):
    # Start Of Engine
    attempt = 3
    while attempt:
        try:
            pool = await open_pool(transactions_path=genesis_path)
        except:
            log("Pool Timed Out! Trying again...")
            if not attempt:
                print("Unable to get pool Response! 3 attempts where made. Exiting...")
                exit()
            attempt -= 1
            continue
        break

    result = []
    verifiers = {}

    if ident:
        request = build_get_validator_info_request(ident.did)
        ident.sign_request(request)
    else:
        request = build_get_txn_request(None, 1, 1)

    from_nodes = []
    if nodes:
        from_nodes = nodes.split(",")
    response = await pool.submit_action(request, node_aliases = from_nodes)
    try:
        # Introduced in https://github.com/hyperledger/indy-vdr/commit/ce0e7c42491904e0d563f104eddc2386a52282f7
        verifiers = await pool.get_verifiers()
    except AttributeError:
        pass
    # End Of Engine

    result = await monitor_plugins.apply_all_plugins_on_value(result, network_name, response, verifiers)
    print(json.dumps(result, indent=2))

def get_script_dir():
    return os.path.dirname(os.path.realpath(__file__))
              
def download_genesis_file(url: str, target_local_path: str):
    log("Fetching genesis file ...")
    target_local_path = f"{get_script_dir()}/genesis.txn"
    urllib.request.urlretrieve(url, target_local_path)

def load_network_list():
    with open(f"{get_script_dir()}/networks.json") as json_file:
        networks = json.load(json_file)
    return networks

def list_networks():
    networks = load_network_list()
    return networks.keys()