import os
import argparse

from typing import Optional
from fastapi import FastAPI, Header

from util import (
    enable_verbose,
#    log,
    create_did
)

from pool import PoolCollection
from fetch_status import FetchStatus
from plugin_collection import PluginCollection

APP_NAME='test_name'
APP_DESCRIPTION='test_description'
APP_VERSION='app_version'

# https://fastapi.tiangolo.com/tutorial/metadata/
app = FastAPI(
    title = APP_NAME,
    description = APP_DESCRIPTION,
    version = APP_VERSION
)

default_args = None
monitor_plugins = None

def set_plugin_parameters(status: bool = False, alerts: bool = False):
    # Store args and monitor_plugins for lazy loading.
    global default_args

    if not default_args:
        # Create plugin instance and set default args
        default_monitor_plugins = PluginCollection('plugins')
        parser = argparse.ArgumentParser()
        parser.add_argument("-v", "--verbose", default=(os.environ.get('VERBOSE', 'False').lower() == 'true'), action="store_true")
        default_monitor_plugins.get_parse_args(parser)
        default_args, unknown = parser.parse_known_args()
        enable_verbose(default_args.verbose)

    # Create namespace with default args
    api_args = argparse.Namespace()
    for name, value in default_args._get_kwargs():
        setattr(api_args, name, value)

    setattr(api_args, 'status', status)
    setattr(api_args, 'alerts', alerts)

    monitor_plugins = PluginCollection('plugins') 
    monitor_plugins.load_all_parse_args(api_args)

    return monitor_plugins

@app.get("/networks")
async def networks():
    data = PoolCollection.load_network_list()
    return data

@app.get("/networks/{network}")
async def network(network, status: bool = False, alerts: bool = False, seed: Optional[str] = Header(None)):
    monitor_plugins = set_plugin_parameters(status, alerts)
    ident = create_did(seed)
    pool_collection = PoolCollection(default_args.verbose)
    network_info = pool_collection.get_network_info(network=network)
    status = FetchStatus(default_args.verbose, pool_collection, monitor_plugins, ident)
    result = await status.fetch(network_info=network_info)
    return result

@app.get("/networks/{network}/{node}")
async def node(network, node, status: bool = False, alerts: bool = False, seed: Optional[str] = Header(None)):
    monitor_plugins = set_plugin_parameters(status, alerts)
    
    ident = create_did(seed)
    pool_collection = PoolCollection(default_args.verbose)
    network_info = pool_collection.get_network_info(network=network)
    status = FetchStatus(default_args.verbose, pool_collection, monitor_plugins, ident)
    result = await status.fetch(network_info, node)
    # result = await status.fetch(network_info, ident, node)
    
    return result