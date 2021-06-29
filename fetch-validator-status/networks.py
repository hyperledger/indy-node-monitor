import os
import json
import urllib.request
import sys
import re
from collections import namedtuple
from util import log
from singleton import Singleton

Network = namedtuple('Network', ['id', 'name', 'genesis_url', 'genesis_path'])

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
    def ids(self):
        return self._networks.keys()

    @property
    def networks(self):
        return self._networks

    @staticmethod
    def get_ids():
        networks = Networks()
        return networks.ids

    @staticmethod
    def get_networks():
        networks = Networks()
        return networks.networks

    @staticmethod
    def __download_genesis_file(genesis_url: str, destination_path: str):
        log("Fetching genesis file ...")
        urllib.request.urlretrieve(genesis_url, destination_path)

    def resolve(self, network_id: str = None, genesis_url: str = None, genesis_path: str = None):
        network_name = None
        genesis_path_base = f"{self.__get_script_dir()}/"

        if network_id and network_id in self.ids:
            log("Connecting to '{0}' ...".format(self.networks[network_id]["name"]))
            network_name = self.networks[network_id]["name"]
            genesis_url = self.networks[network_id]["genesisUrl"]
            if 'genesisPath' in self.networks[network_id]:
                genesis_path = self.networks[network_id]['genesisPath']

        if genesis_url:
            if not network_name:
                network_name = genesis_url
                network_id = network_name
                log(f"Setting network name = {network_name} ...")

            if not genesis_path:
                # Remove and replace parts of the string to make a valid path based on the network name.
                sub_path = network_name.replace("https://", "")
                sub_path = re.sub('[ /.]', '_', sub_path)
                genesis_path = f"{genesis_path_base}{sub_path}/"
                if not os.path.exists(genesis_path):
                    os.makedirs(genesis_path)
                genesis_path = f"{genesis_path}genesis.txn"
                Networks.__download_genesis_file(genesis_url, genesis_path)
                self._networks[network_id] = {'name': network_name, 'genesisUrl': genesis_url, 'genesisPath': genesis_path}

        if not os.path.exists(genesis_path):
            print("Set the GENESIS_URL or GENESIS_PATH environment variable or argument.\n", file=sys.stderr)
            exit()

        network = Network(network_id, network_name, genesis_url, genesis_path)
        return network