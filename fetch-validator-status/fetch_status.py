from indy_vdr.ledger import (
    build_get_validator_info_request,
    build_get_txn_request,
)
from util import log
from plugin_collection import PluginCollection
from DidKey import DidKey
from pool import PoolCollection

class FetchStatus():
    def __init__(self, verbose, pool_collection: PoolCollection):
        self.verbose = verbose
        self.pool_collection = pool_collection

    async def fetch(self, network, monitor_plugins: PluginCollection, nodes: str = None, ident: DidKey = None):
        result = []
        verifiers = {}

        network_info = self.pool_collection.get_network_info(network=network)
        pool = await self.pool_collection.get_pool(network_info)

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

        log("Passing results to plugins for processing ...")
        result = await monitor_plugins.apply_all_plugins_on_value(result, network_info.network_name, response, verifiers)
        log("Processing complete.")
        return result