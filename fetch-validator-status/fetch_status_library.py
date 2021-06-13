import json
import os
import sys
from collections import namedtuple

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
            log("Connecting to Pool ...")
            pool = await open_pool(transactions_path=genesis_path)
        except:
            log("Pool Timed Out! Trying again ...")
            if not attempt:
                print("Unable to get pool Response! 3 attempts where made. Exiting ...")
                exit()
            attempt -= 1
            continue
        else:
            log("Connected to Pool ...")
        break

    result = []
    verifiers = {}

    if ident:
        log(f"Building request with did: {ident.did} ...")
        request = build_get_validator_info_request(ident.did)
        ident.sign_request(request)
    else:
        log("Building anonymous request ...")
        request = build_get_txn_request(None, 1, 1)

    from_nodes = []
    if nodes:
        from_nodes = nodes.split(",")
        log("Submitting request ...")

    response = await pool.submit_action(request, node_aliases = from_nodes)
    
    try:
        # Introduced in https://github.com/hyperledger/indy-vdr/commit/ce0e7c42491904e0d563f104eddc2386a52282f7
        log("Getting list of verifiers ...")
        verifiers = await pool.get_verifiers()
    except AttributeError:
        log("Unable to get list of verifiers. Plesase make sure you have the latest verson of indy-vdr.")
        pass
    # End Of Engine

    log("Passing results to plugins for processing ...")
    result = await monitor_plugins.apply_all_plugins_on_value(result, network_name, response, verifiers)
    log("Processing complete.")
    return result

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

def init_network_args(network: str = None, genesis_url: str = None, genesis_path: str = None):
    if not genesis_path:
        genesis_path = f"{get_script_dir()}/genesis.txn"

    if network:
        log("Loading known network list ...")
        networks = load_network_list()
        if network in networks:
            log("Connecting to '{0}' ...".format(networks[network]["name"]))
            genesis_url = networks[network]["genesisUrl"]
            network_name = networks[network]["name"]

    if genesis_url:
        download_genesis_file(genesis_url, genesis_path)
        if not network_name:
            network_name = genesis_url
            log(f"Setting network name  = {network_name} ...")

    if not os.path.exists(genesis_path):
        print("Set the GENESIS_URL or GENESIS_PATH environment variable or argument.\n", file=sys.stderr)
        exit()

    Network_Info = namedtuple('Network_Info', ['network_name', 'genesis_url', 'genesis_path']) 
    network_info = Network_Info(network_name, genesis_url, genesis_path)

    return network_info

def create_did(seed):
    ident = None
    if seed:
        try:
            ident = DidKey(seed)
            log("DID:", ident.did, " Verkey:", ident.verkey)
        except:
            log("Invalid seed.  Continuing anonymously ...")
    return ident