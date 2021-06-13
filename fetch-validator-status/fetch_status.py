from indy_vdr.ledger import (
    build_get_validator_info_request,
    build_get_txn_request,
)
from util import log
from plugin_collection import PluginCollection
from DidKey import DidKey
from pool import PoolCollection

class FetchStatus():
    def __init__(self, verbose, pool_collection: PoolCollection, monitor_plugins: PluginCollection, ident: DidKey = None):
        self.verbose = verbose
        self.pool_collection = pool_collection
        self.monitor_plugins = monitor_plugins
        self.ident = ident

    async def fetch(self, network_info, nodes: str = None):
        result = []
        verifiers = {}

        pool = await self.pool_collection.get_pool(network_info)

        if self.ident:
            log(f"Building request with did: {self.ident.did} ...")
            request = build_get_validator_info_request(self.ident.did)
            self.ident.sign_request(request)
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

        log("Passing results to plugins for processing ...")
        result = await self.monitor_plugins.apply_all_plugins_on_value(result, network_info.network_name, response, verifiers)
        log("Processing complete.")
        return result