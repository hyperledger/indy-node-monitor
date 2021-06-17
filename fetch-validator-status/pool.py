import os
import json
import urllib.request
import sys
import asyncio
import re
from collections import namedtuple
from util import log
from indy_vdr.pool import open_pool
from singleton import Singleton
        
class PoolCollection(object, metaclass=Singleton):
    def __init__(self, verbose):
        self.verbose = verbose
        self.network_cache = {}
        self.lock = asyncio.Lock()

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
        # Network pool connection cache with async thread lock for REST API.
        async with self.lock:
            if network_info.network_name in self.network_cache:
                # Use cache.
                log(f"Pool for {network_info.network_name} found in cache ... ")
                pool = self.network_cache[network_info.network_name]['pool']
            else:        
                # Create cache.
                log(f"Pool for {network_info.network_name} not found in cache, creating new connection ... ")    
                self.network_cache[network_info.network_name] = {}
                self.network_cache[network_info.network_name]['genesis_path'] = network_info.genesis_path
                self.network_cache[network_info.network_name]['genesis_url'] = network_info.genesis_url
                pool = await self.fetch_pool_connection(network_info.genesis_path)
                self.network_cache[network_info.network_name]['pool'] = pool
            return pool

    def get_network_info(self, network: str = None, genesis_url: str = None, genesis_path: str = None):
        network_name = None
        genesis_path_base = f"{PoolCollection.get_script_dir()}/"
        
        if network:
            log("Loading known network list ...")
            networks = PoolCollection.load_network_list()
            if network in networks:
                log("Connecting to '{0}' ...".format(networks[network]["name"]))
                genesis_url = networks[network]["genesisUrl"]
                network_name = networks[network]["name"]

        if genesis_url:
            if not network_name:
                network_name = genesis_url
                log(f"Setting network name = {network_name} ...")
            if not genesis_path:
                # Remove and replace parts of the string to make a file name to create the path.
                network_name_path = network_name.replace("https://", "")
                network_name_path = re.sub('[ /.]', '_', network_name_path)
                genesis_path = f"{genesis_path_base}{network_name_path}/"
                if not os.path.exists(genesis_path):
                    os.makedirs(genesis_path)
                genesis_path = f"{genesis_path}genesis.txn"

            self.download_genesis_file(genesis_url, genesis_path)
        if not os.path.exists(genesis_path):
            print("Set the GENESIS_URL or GENESIS_PATH environment variable or argument.\n", file=sys.stderr)
            exit()

        Network_Info = namedtuple('Network_Info', ['network_name', 'genesis_url', 'genesis_path']) 
        network_info = Network_Info(network_name, genesis_url, genesis_path)

        return network_info

    def download_genesis_file(self, url: str, target_local_path: str):
        log("Fetching genesis file ...")
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
