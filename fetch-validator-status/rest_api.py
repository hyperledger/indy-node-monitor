import os
import argparse
from typing import Optional
from fastapi import FastAPI, Header, HTTPException
from starlette.responses import RedirectResponse
from util import (
    enable_verbose,
#    log,
    create_did
)
from pool import PoolCollection
from networks import Networks
from fetch_status import FetchStatus, NodeNotFound
from plugin_collection import PluginCollection

APP_NAME='Node Monitor'
APP_DESCRIPTION='test_description'
APP_VERSION='0.0.0'

# https://fastapi.tiangolo.com/tutorial/metadata/
app = FastAPI(
    title = APP_NAME,
    description = APP_DESCRIPTION,
    version = APP_VERSION
)

# global variables
default_args = None
monitor_plugins = None
pool_collection = None
node_info = None

def set_plugin_parameters(status: bool = False, alerts: bool = False):
    # Store args and monitor_plugins for lazy loading.
    global default_args, pool_collection, node_info

    if not default_args:
        # Create plugin instance and set default args
        default_monitor_plugins = PluginCollection('plugins')
        parser = argparse.ArgumentParser()
        parser.add_argument("-v", "--verbose", default=(os.environ.get('VERBOSE', 'False').lower() == 'true'), action="store_true")
        default_monitor_plugins.get_parse_args(parser)
        default_args, unknown = parser.parse_known_args()
        enable_verbose(default_args.verbose)
        pool_collection = PoolCollection(default_args.verbose, Networks())
        node_info = FetchStatus(default_args.verbose, pool_collection)

    # Create namespace with default args and load them into api_args
    api_args = argparse.Namespace()
    for name, value in default_args._get_kwargs():
        setattr(api_args, name, value)

    # Set api_args with the values from the parameters
    setattr(api_args, 'status', status)
    setattr(api_args, 'alerts', alerts)

    # Create and load plugins with api_args
    monitor_plugins = PluginCollection('plugins')
    monitor_plugins.load_all_parse_args(api_args)

    return monitor_plugins

# Redirect users to the '/docs' page but don't include this endpoint in the docs.
@app.get("/", include_in_schema=False)
async def redirect():
    response = RedirectResponse(url='/docs')
    return response

@app.get("/networks")
async def networks():
    data = Networks.get_networks()
    return data

@app.get("/networks/{network}")
async def network(network, status: bool = False, alerts: bool = False, seed: Optional[str] = Header(None)):
    monitor_plugins = set_plugin_parameters(status, alerts)
    ident = create_did(seed)
    result = await node_info.fetch(network_id=network, monitor_plugins=monitor_plugins, ident=ident)
    return result

@app.get("/networks/{network}/{node}")
async def node(network, node, status: bool = False, alerts: bool = False, seed: Optional[str] = Header(None)):
    monitor_plugins = set_plugin_parameters(status, alerts)
    ident = create_did(seed)
    try:
        result = await node_info.fetch(network_id=network, monitor_plugins=monitor_plugins, nodes=node, ident=ident)
    except NodeNotFound as error:
        print(error)
        raise HTTPException(status_code=400, detail=str(error))

    return result