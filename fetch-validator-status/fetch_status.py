import argparse
import asyncio
import base58
import base64
import json
import os
import sys
import datetime
import urllib.request
from typing import Tuple

import nacl.signing

import indy_vdr
from indy_vdr.ledger import (
    build_get_validator_info_request,
    build_get_txn_request,
    Request,
)
from indy_vdr.pool import open_pool


verbose = False


def log(*args):
    if verbose:
        print(*args, "\n", file=sys.stderr)

class DidKey:
    def __init__(self, seed):
        seed = seed_as_bytes(seed)
        self.sk = nacl.signing.SigningKey(seed)
        self.vk = bytes(self.sk.verify_key)
        self.did = base58.b58encode(self.vk[:16]).decode("ascii")
        self.verkey = base58.b58encode(self.vk).decode("ascii")

    def sign_request(self, req: Request):
        signed = self.sk.sign(req.signature_input)
        req.set_signature(signed.signature)


def seed_as_bytes(seed):
    if not seed or isinstance(seed, bytes):
        return seed
    if len(seed) != 32:
        return base64.b64decode(seed)
    return seed.encode("ascii")


async def fetch_status(genesis_path: str, nodes: str = None, ident: DidKey = None, status_only: bool = False):
    pool = await open_pool(transactions_path=genesis_path)
    result = []

    if ident:
        request = build_get_validator_info_request(ident.did)
        ident.sign_request(request)
    else:
        request = build_get_txn_request(None, 1, 1)

    from_nodes = []
    if nodes:
        from_nodes = nodes.split(",")
    response = await pool.submit_action(request, node_aliases = from_nodes)

    primary = ""
    packages = {}
    for node, val in response.items():
        jsval = []
        status = {}
        errors = []
        warnings = []
        entry = {"name": node}
        try:
            jsval = json.loads(val)
            if not primary:
                primary = await get_primary_name(jsval, node)
            errors, warnings = await detect_issues(jsval, node, primary, ident)
            packages[node] = await get_package_info(jsval)
        except json.JSONDecodeError:
            errors = [val]  # likely "timeout"

        # Status Summary
        entry["status"] = await get_status_summary(jsval, errors)
        # Errors / Warnings
        if len(errors) > 0:
            entry["status"]["errors"] = len(errors)
            entry["errors"] = errors
        if len(warnings) > 0:
            entry["status"]["warnings"] = len(warnings)
            entry["warnings"] = warnings
        # Full Response
        if not status_only and jsval:
            entry["response"] = jsval

        result.append(entry)

    # Package Mismatches
    if packages:
        await merge_package_mismatch_info(result, packages)

    # Connection Issues
    await detect_connection_issues(result)

    print(json.dumps(result, indent=2))


async def detect_connection_issues(result: any) -> any:

    for node in result:
        connection_errors = []
        node_name = node["name"]
        if "warnings" in node:
            for warning in node["warnings"]:
                if "Unreachable_nodes" in warning :
                    for item in warning["Unreachable_nodes"]:
                        # This is the name of the unreachable node.  Now we need to determine whether that node can't see the current one.
                        # If the nodes can't see each other, upgrade to an error condition.
                        unreachable_node_name = item[0]
                        unreachable_node = [t for t in result if t["name"] == unreachable_node_name][0]
                        if "warnings" in unreachable_node:
                            for unreachable_node_warning in unreachable_node["warnings"]:
                                if "Unreachable_nodes" in unreachable_node_warning :
                                    for unreachable_node_item in unreachable_node_warning["Unreachable_nodes"]:
                                        if unreachable_node_item[0] == node_name:
                                            connection_errors.append(node_name + " and " + unreachable_node_name + " can't reach each other.")
        # Merge errors and update status
        if connection_errors:
            if "errors" in node:
                for item in connection_errors:
                    node["errors"].append(item)
            else:
                node["errors"] = connection_errors
            node["status"]["errors"] = len(node["errors"])
            node["status"]["ok"] = (len(node["errors"]) <= 0)


async def get_primary_name(jsval: any, node: str) -> str:
    primary = ""
    if "REPLY" in jsval["op"]:
        if "Node_info" in jsval["result"]["data"]:
            primary = jsval["result"]["data"]["Node_info"]["Replicas_status"][node+":0"]["Primary"]
    return primary


async def get_status_summary(jsval: any, errors: list) -> any:
    status = {}
    status["ok"] = (len(errors) <= 0)
    if jsval and ("REPLY" in jsval["op"]):
        if "Node_info" in jsval["result"]["data"]:
            status["uptime"] = str(datetime.timedelta(seconds = jsval["result"]["data"]["Node_info"]["Metrics"]["uptime"]))
        if "timestamp" in jsval["result"]["data"]:
            status["timestamp"] = jsval["result"]["data"]["timestamp"]
        if "Software" in jsval["result"]["data"]:
            status["software"] = {}
            status["software"]["indy-node"] = jsval["result"]["data"]["Software"]["indy-node"]
            status["software"]["sovrin"] = jsval["result"]["data"]["Software"]["sovrin"]

    return status

async def get_package_info(jsval: any) -> any:
    packages = {}
    if jsval and ("REPLY" in jsval["op"]):
        if "Software" in jsval["result"]["data"]:
            for installed_package in jsval["result"]["data"]["Software"]["Installed_packages"]:
                package, version = installed_package.split()
                packages[package] = version

    return packages

async def check_package_versions(packages: any) -> any:
    warnings = {}
    for node, package_list in packages.items():
        mismatches = []
        for package, version in package_list.items():
            total = 0
            same = 0
            other_version = ""
            for comp_node, comp_package_list in packages.items():
                if package in comp_package_list:
                    total +=1
                    comp_version = comp_package_list[package]
                    if comp_version == version:
                        same +=1
                    else:
                        other_version = comp_version
            if (same/total) < .5:
                mismatches.append("Package mismatch: '{0}' has '{1}' {2}, while most other nodes have '{1}' {3}".format(node, package, version, other_version))
        if mismatches:
            warnings[node] = mismatches
    return warnings

async def merge_package_mismatch_info(result: any, packages: any):
    package_warnings = await check_package_versions(packages)
    if package_warnings:
        for node_name in package_warnings:
            entry_to_update = [t for t in result if t["name"] == node_name][0]
            if "warnings" in entry_to_update:
                for item in package_warnings[node_name]:
                    entry_to_update["warnings"].append(item)
            else:
                entry_to_update["warnings"] = package_warnings[node_name]
            entry_to_update["status"]["warnings"] = len(entry_to_update["warnings"])

async def detect_issues(jsval: any, node: str, primary: str, ident: DidKey = None) -> Tuple[any, any]:
    errors = []
    warnings = []
    ledger_sync_status={}
    if "REPLY" in jsval["op"]:
        if ident:
            # Ledger Write Consensus Issues
            if not jsval["result"]["data"]["Node_info"]["Freshness_status"]["0"]["Has_write_consensus"]:
                errors.append("Config Ledger Has_write_consensus: {0}".format(jsval["result"]["data"]["Node_info"]["Freshness_status"]["0"]["Has_write_consensus"]))
            if not jsval["result"]["data"]["Node_info"]["Freshness_status"]["1"]["Has_write_consensus"]:
                errors.append("Main Ledger Has_write_consensus: {0}".format(jsval["result"]["data"]["Node_info"]["Freshness_status"]["1"]["Has_write_consensus"]))
            if not jsval["result"]["data"]["Node_info"]["Freshness_status"]["2"]["Has_write_consensus"]:
                errors.append("Pool Ledger Has_write_consensus: {0}".format(jsval["result"]["data"]["Node_info"]["Freshness_status"]["2"]["Has_write_consensus"]))
            if "1001" in  jsval["result"]["data"]["Node_info"]["Freshness_status"]:
                if not jsval["result"]["data"]["Node_info"]["Freshness_status"]["1001"]["Has_write_consensus"]:
                    errors.append("Token Ledger Has_write_consensus: {0}".format(jsval["result"]["data"]["Node_info"]["Freshness_status"]["1001"]["Has_write_consensus"]))

            # Ledger Status
            for ledger, status in jsval["result"]["data"]["Node_info"]["Catchup_status"]["Ledger_statuses"].items():
                if status != "synced":
                    ledger_sync_status[ledger] = status
            if ledger_sync_status:
                ledger_status = {}
                ledger_status["ledger_status"] = ledger_sync_status
                ledger_status["ledger_status"]["transaction-count"] = jsval["result"]["data"]["Node_info"]["Metrics"]["transaction-count"]
                warnings.append(ledger_status)

            # Mode
            if jsval["result"]["data"]["Node_info"]["Mode"] != "participating":
                warnings.append("Mode: {0}".format(jsval["result"]["data"]["Node_info"]["Mode"]))

            # Primary Node Mismatch
            if jsval["result"]["data"]["Node_info"]["Replicas_status"][node+":0"]["Primary"] != primary:
                warnings.append("Primary Mismatch! This Nodes Primary: {0} (Expected: {1})".format(jsval["result"]["data"]["Node_info"]["Replicas_status"][node+":0"]["Primary"], primary))

            # Unreachable Nodes
            if jsval["result"]["data"]["Pool_info"]["Unreachable_nodes_count"] > 0:
                warnings.append({"Unreachable_nodes": jsval["result"]["data"]["Pool_info"]["Unreachable_nodes"]})

            # Denylisted Nodes
            if len(jsval["result"]["data"]["Pool_info"]["Blacklisted_nodes"]) > 0:
                warnings.append("Denylisted Nodes: {1}".format(jsval["result"]["data"]["Pool_info"]["Blacklisted_nodes"]))
    else:
        if "reason" in jsval:
            errors.append(jsval["reason"])
        else:
            errors.append("unknown error")

    return errors, warnings


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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch the status of all the indy-nodes within a given pool.")
    parser.add_argument("--net", choices=list_networks(), help="Connect to a known network using an ID.")
    parser.add_argument("--list-nets", action="store_true", help="List known networks.")
    parser.add_argument("--genesis-url", default=os.environ.get('GENESIS_URL') , help="The url to the genesis file describing the ledger pool.  Can be specified using the 'GENESIS_URL' environment variable.")
    parser.add_argument("--genesis-path", default=os.getenv("GENESIS_PATH") or f"{get_script_dir()}/genesis.txn" , help="The path to the genesis file describing the ledger pool.  Can be specified using the 'GENESIS_PATH' environment variable.")
    parser.add_argument("-s", "--seed", default=os.environ.get('SEED') , help="The privileged DID seed to use for the ledger requests.  Can be specified using the 'SEED' environment variable.")
    parser.add_argument("-a", "--anonymous", action="store_true", help="Perform requests anonymously, without requiring privileged DID seed.")
    parser.add_argument("--status", action="store_true", help="Get status only.  Suppresses detailed results.")
    parser.add_argument("--nodes", help="The comma delimited list of the nodes from which to collect the status.  The default is all of the nodes in the pool.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    args = parser.parse_args()

    verbose = args.verbose

    if args.list_nets:
        print(json.dumps(load_network_list(), indent=2))
        exit()

    if args.net:
        log("Loading known network list ...")
        networks = load_network_list()
        if args.net in networks:
            log("Connecting to '{0}' ...".format(networks[args.net]["name"]))
            args.genesis_url = networks[args.net]["genesisUrl"]

    if args.genesis_url:
        download_genesis_file(args.genesis_url, args.genesis_path)
    if not os.path.exists(args.genesis_path):
        print("Set the GENESIS_URL or GENESIS_PATH environment variable or argument.\n", file=sys.stderr)
        parser.print_help()
        exit()

    did_seed = None if args.anonymous else args.seed
    if not did_seed and not args.anonymous:
        print("Set the SEED environment variable or argument, or specify the anonymous flag.\n", file=sys.stderr)
        parser.print_help()
        exit()

    log("indy-vdr version:", indy_vdr.version())
    if did_seed:
        ident = DidKey(did_seed)
        log("DID:", ident.did, " Verkey:", ident.verkey)
    else:
        ident = None

    asyncio.get_event_loop().run_until_complete(fetch_status(args.genesis_path, args.nodes, ident, args.status))