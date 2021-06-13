import os
import json
import urllib.request
import sys
from collections import namedtuple
from util import log
from indy_vdr.pool import open_pool

class PoolCollection(object):
    def __init__(self, verbose):
        self.verbose = verbose

    async def fetch_pool_connection(self, genesis_path):
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
        return pool

    async def get_pool(self, network_info):
        # manage dict
        # get network_info use as key
        # look into dict with network_info as tupl or network_info.network_name as key
        # if key found return value pool
        # other wise fetch pool connection
        # add value to dict with key 
        # return value

        return await self.fetch_pool_connection(network_info.genesis_path)

    def get_network_info(self, network: str = None, genesis_url: str = None, genesis_path: str = None):
        if not genesis_path:
            genesis_path = f"{PoolCollection.get_script_dir()}/genesis.txn" # use as base dir save file with using network name or genesis url

        if network:
            log("Loading known network list ...")
            networks = PoolCollection.load_network_list()
            if network in networks:
                log("Connecting to '{0}' ...".format(networks[network]["name"]))
                genesis_url = networks[network]["genesisUrl"]
                network_name = networks[network]["name"] # if dosen't exist brake down the url ^

        if genesis_url:
            self.download_genesis_file(genesis_url, genesis_path)
            if not network_name:
                network_name = genesis_url
                log(f"Setting network name = {network_name} ...")

        if not os.path.exists(genesis_path):
            print("Set the GENESIS_URL or GENESIS_PATH environment variable or argument.\n", file=sys.stderr)
            exit()

        Network_Info = namedtuple('Network_Info', ['network_name', 'genesis_url', 'genesis_path']) 
        network_info = Network_Info(network_name, genesis_url, genesis_path)

        return network_info

    def download_genesis_file(self, url: str, target_local_path: str):
        log("Fetching genesis file ...")
        target_local_path = f"{PoolCollection.get_script_dir()}/genesis.txn"
        urllib.request.urlretrieve(url, target_local_path)

    @staticmethod
    def get_script_dir():
        return os.path.dirname(os.path.realpath(__file__))

    @staticmethod
    def load_network_list():
        with open(f"{PoolCollection.get_script_dir()}/networks.json") as json_file:
            networks = json.load(json_file)
        return networks

    @staticmethod
    def list_networks():
        networks = PoolCollection.load_network_list()
        return networks.keys()
