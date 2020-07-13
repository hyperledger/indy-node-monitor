import asyncio
import base58
import base64
import json
import os
import sys
import urllib.request
import time

import nacl.signing

import indy_vdr
from indy_vdr.ledger import build_get_validator_info_request, Request
from indy_vdr.pool import open_pool

from prometheus_exporter import PrometheusExporter

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


async def fetch_status(genesis_path: str, ident: DidKey):
    pool = await open_pool(transactions_path=genesis_path)

    req = build_get_validator_info_request(ident.did)
    ident.sign_request(req)
    result = await pool.submit_action(req)
    for node, val in result.items():
        try:
            jsval = json.loads(val)
            result[node] = jsval
        except json.JSONDecodeError:
            pass 
    print(json.dumps(result, indent=2))
    return result

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
    did_seed = os.getenv("SEED")
    if not did_seed:
        raise ValueError("Set the SEED environment variable")

    log("indy-vdr version:", indy_vdr.version())
    ident = DidKey(did_seed)
    log("DID:", ident.did, " Verkey:", ident.verkey)

    prom = PrometheusExporter(8000)
    prom.start()

    while True:
        result = asyncio.get_event_loop().run_until_complete(fetch_status(genesis_path, ident))
        prom.update(result)
        time.sleep(5)