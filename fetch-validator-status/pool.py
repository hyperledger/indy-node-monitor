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


Network = namedtuple('Network', ['name', 'genesis_url', 'genesis_path'])

class Networks(object, metaclass=Singleton):
    def __init__(self):
        self._networks = self.__load_network_list()

    def __get_script_dir(self):
        return os.path.dirname(os.path.realpath(__file__))

    def __load_network_list(self):
        log("Loading known network list ...")
        with open(f"{self.__get_script_dir()}/networks.json") as json_file:
            networks = json.load(json_file)
        return networks

    @property
    def names(self):
        return self._networks.keys()

    @property
    def networks(self):
        return self._networks

    @staticmethod
    def get_names():
        networks = Networks()
        return networks.names

    @staticmethod
    def get_all():
        networks = Networks()
        return networks.networks

    @staticmethod
    def __download_genesis_file(url: str, target_local_path: str):
        log("Fetching genesis file ...")
        urllib.request.urlretrieve(url, target_local_path)

    # ToDo:
    #   - Refactor to maintain the list of networks dynamically using self._networks
    #   - In the case a network does not existing the list add it.
    #       - For example in the case a user provides a genesis_url or genesis_path rather than a named named (known) network.
    #       - The key for the network should be dynamically generated, could simply be Network#; Network1, Network2, etc.
    #   - As genesis files are downloaded (or provided) the entries should be updated with the genesis_path information.
    #   - Genesis files should only be downloaded for entries without genesis_path info.
    def resolve(self, network: str = None, genesis_url: str = None, genesis_path: str = None):
        network_id = None
        genesis_path_base = f"{self.__get_script_dir()}/"

        if network:
            if network in self.names:
                log("Connecting to '{0}' ...".format(self.networks[network]["name"]))
                genesis_url = self.networks[network]["genesisUrl"]
                network_id = self.networks[network]["name"]

        if genesis_url:
            if not network_id:
                network_id = genesis_url
                log(f"Setting network name = {network_id} ...")
            if not genesis_path:
                # Remove and replace parts of the string to make a file name to create the path.
                network_id_path = network_id.replace("https://", "")
                network_id_path = re.sub('[ /.]', '_', network_id_path)
                genesis_path = f"{genesis_path_base}{network_id_path}/"
                if not os.path.exists(genesis_path):
                    os.makedirs(genesis_path)
                genesis_path = f"{genesis_path}genesis.txn"

            Networks.__download_genesis_file(genesis_url, genesis_path)
        if not os.path.exists(genesis_path):
            print("Set the GENESIS_URL or GENESIS_PATH environment variable or argument.\n", file=sys.stderr)
            exit()

        network = Network(network_id, genesis_url, genesis_path)

        return network


class PoolCollection(object, metaclass=Singleton):
    def __init__(self, verbose, networks: Networks):
        self.verbose = verbose
        self.networks = networks
        self.pool_cache = {}
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

    # ToDo:
    #   - Once Networks.resolve is fully fleshed out and the Networks class managaes all of the network properties
    #     this class no longer has to manage the 'genesis_path' and 'genesis_url' properties, it can use the 
    #     networks instance for lookup, and cache and look up information by network key rather than network name; 
    #     Networks.names (the network keys), rather than full Networks.networks[key].name (network name).
    async def get_pool(self, network_id):
        network = self.networks.resolve(network_id)
        # Network pool connection cache with async thread lock for REST API.
        async with self.lock:
            if network.name in self.pool_cache:
                # Use cache.
                log(f"Pool for {network.name} found in cache ... ")
                pool = self.pool_cache[network.name]['pool']
            else:
                # Create cache.
                log(f"Pool for {network.name} not found in cache, creating new connection ... ")
                self.pool_cache[network.name] = {}
                self.pool_cache[network.name]['genesis_path'] = network.genesis_path
                self.pool_cache[network.name]['genesis_url'] = network.genesis_url
                pool = await self.fetch_pool_connection(network.genesis_path)
                self.pool_cache[network.name]['pool'] = pool
            return pool, network.name