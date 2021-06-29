import asyncio
from util import log
from indy_vdr.pool import open_pool
from singleton import Singleton
from networks import Networks

class PoolCollection(object, metaclass=Singleton):
    def __init__(self, verbose, networks: Networks):
        self.verbose = verbose
        self.networks = networks
        self.pool_cache = {}
        self.lock = asyncio.Lock()

    async def __fetch_pool_connection(self, genesis_path):
        attempt = 3
        while attempt:
            try:
                log("Connecting to Pool ...")
                pool = await open_pool(transactions_path=genesis_path)
            except:
                log("Pool Timed Out! Trying again ...")
                if not attempt:
                    print("Unable to get response from pool!  3 attempts where made.  Exiting ...")
                    exit()
                attempt -= 1
                continue
            else:
                log("Connected to Pool ...")
            break
        return pool

    async def get_pool(self, network_id):
        network = self.networks.resolve(network_id)
        # Network pool connection cache with async thread lock for REST API.
        async with self.lock:
            if network.id in self.pool_cache:
                # Cache hit ...
                log(f"The pool for {network.name} was found in the cache ...")
                pool = self.pool_cache[network.id]['pool']
            else:
                # Cache miss ...
                log(f"A pool for {network.name} was not found in the cache, creating new connection ...")
                pool = await self.__fetch_pool_connection(network.genesis_path)
                self.pool_cache[network.id] = {}
                self.pool_cache[network.id]['pool'] = pool
                log(f"Cached the pool for {network.name} ...")
            return pool, network.name