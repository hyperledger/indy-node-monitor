import asyncio
import base58
import base64
import json
import os
import sys
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


def log(*args):
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


async def fetch_status(genesis_path: str, ident: DidKey = None):
    pool = await open_pool(transactions_path=genesis_path)
    result = []

    if ident:
        request = build_get_validator_info_request(ident.did)
        ident.sign_request(request)
    else:
        request = build_get_txn_request(None, 1, 1)

    response = await pool.submit_action(request)

    primary = ""
    for node, val in response.items():
        errors = []
        warnings = []
        entry = {"name": node}
        try:
            jsval = json.loads(val)
            if not primary:
                primary = await get_primary_name(jsval, node)
            errors, warnings = await detect_issues(jsval, node, primary, ident)
            entry["response"] = jsval
        except json.JSONDecodeError:
            errors = [val]  # likely "timeout"

        status = {}
        status["ok"] = (len(errors) <= 0)
        status["errors"] = len(errors)
        status["warnings"] = len(warnings)
        entry["status"] = status
        
        if len(errors) > 0:
            entry["errors"] = errors
        if len(warnings) > 0:
            entry["warnings"] = warnings

        result.append(entry)

    print(json.dumps(result, indent=2))

async def get_primary_name(jsval: any, node: str) -> str:
    primary = ""
    if "REPLY" in jsval["op"]:
        if "Node_info" in jsval["result"]["data"]:
            primary = jsval["result"]["data"]["Node_info"]["Replicas_status"][node+":0"]["Primary"]
    return primary

async def detect_issues(jsval: any, node: str, primary: str, ident: DidKey = None) -> Tuple[any, any]:
    errors = []
    warnings = []
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

            # Primary Node Mismatch
            if jsval["result"]["data"]["Node_info"]["Replicas_status"][node+":0"]["Primary"] != primary:
                warnings.append("Primary Mismatch! This Nodes Primary: {0} (Expected: {1})".format(jsval["result"]["data"]["Node_info"]["Replicas_status"][node+":0"]["Primary"], primary))

            # Unreachable Nodes
            if jsval["result"]["data"]["Pool_info"]["Total_nodes_count"] != jsval["result"]["data"]["Pool_info"]["Reachable_nodes_count"]:
                warnings.append("Unreachable Nodes: The {0} node has Unreachable_nodes_count of {1}; {2}".format(node, jsval["result"]["data"]["Pool_info"]["Unreachable_nodes_count"], jsval["result"]["data"]["Pool_info"]["Unreachable_nodes"]))
    else:
        if "reason" in jsval:
            errors = jsval["reason"]
        else:
            errors = "unknown error"

    return errors, warnings


def get_script_dir():
    return os.path.dirname(os.path.realpath(__file__))


def download_genesis_file(url: str, target_local_path: str):
    log("Fetching genesis file")
    target_local_path = f"{get_script_dir()}/genesis.txn"
    urllib.request.urlretrieve(url, target_local_path)


if __name__ == "__main__":
    genesis_url = os.getenv("GENESIS_URL")
    genesis_path = os.getenv("GENESIS_PATH") or f"{get_script_dir()}/genesis.txn"
    if genesis_url:
        download_genesis_file(genesis_url, genesis_path)
    if not os.path.exists(genesis_path):
        raise ValueError("Set the GENESIS_URL or GENESIS_PATH environment variable")
    anon = "-a" in sys.argv
    did_seed = None if anon else os.getenv("SEED")
    if not did_seed and not anon:
        raise ValueError("Set the SEED environment variable")

    log("indy-vdr version:", indy_vdr.version())
    if did_seed:
        ident = DidKey(did_seed)
        log("DID:", ident.did, " Verkey:", ident.verkey)
    else:
        ident = None

    asyncio.get_event_loop().run_until_complete(fetch_status(genesis_path, ident))
