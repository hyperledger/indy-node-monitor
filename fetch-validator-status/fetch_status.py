from argparse import ArgumentError
from indy_vdr.ledger import (
    build_get_validator_info_request,
    build_get_txn_request,
)
from util import log
from plugin_collection import PluginCollection
from DidKey import DidKey
from pool import PoolCollection
from singleton import Singleton

class NodeNotFound(Exception):
    pass

class FetchStatus(object, metaclass=Singleton):
    def __init__(self, verbose, pool_collection: PoolCollection):
        self.verbose = verbose
        self.pool_collection = pool_collection

    async def fetch(self, network_id: str, monitor_plugins: PluginCollection, nodes: str = None, ident: DidKey = None):
        result = []
        verifiers = {}

        pool, network_name = await self.pool_collection.get_pool(network_id)
        if ident:
            log(f"Building request with did: {ident.did} ...")
            request = build_get_validator_info_request(ident.did)
            ident.sign_request(request)
        else:
            log("Building an anonymous request ...")
            request = build_get_txn_request(None, 1, 1)

        from_nodes = []
        if nodes:
            from_nodes = nodes.split(",")

        try:
            # Introduced in https://github.com/hyperledger/indy-vdr/commit/ce0e7c42491904e0d563f104eddc2386a52282f7
            log("Getting list of verifiers ...")
            verifiers = await pool.get_verifiers()
        except AttributeError:
            log("Unable to get list of verifiers. Please make sure you have the latest version of indy-vdr.")
            pass

        if verifiers and from_nodes:
            for node in from_nodes:
                if not node in verifiers:
                    raise NodeNotFound(f'{node} is not a member of {network_name}.')

        log("Submitting request ...")
        response = await pool.submit_action(request, node_aliases = from_nodes)

        log("Passing results to plugins for processing ...")
        result = await monitor_plugins.apply_all_plugins_on_value(result, network_name, response, verifiers)
        log("Processing complete.")
        return result