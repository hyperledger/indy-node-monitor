import os
import json
import argparse

from typing import Optional
from fastapi import FastAPI, Header
from pydantic import BaseModel
from httpx import AsyncClient

from fetch_status_library import (
    enable_verbose,
    log,
    fetch_status,
    load_network_list,
    init_network_args
)
from DidKey import DidKey
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

args = None
monitor_plugins = None

def set_plugin_parameters(status: bool = False, alerts: bool = False):

    # Store args and monitor_plugins for lazy loading.
    global args
    global monitor_plugins

    if not args:
        # Create plugin instance and set default args
        monitor_plugins = PluginCollection('plugins')
        parser = argparse.ArgumentParser()
        parser.add_argument("-v", "--verbose", default=(os.environ.get('VERBOSE', 'False').lower() == 'true'), action="store_true")
        monitor_plugins.get_parse_args(parser)
        args, unknown = parser.parse_known_args()
        enable_verbose(args.verbose)

    # Create namspace with default args
    api_args = argparse.Namespace()
    for name, value in args._get_kwargs():
        setattr(api_args, name, value)

    setattr(api_args, 'status', status)
    setattr(api_args, 'alerts', alerts)

    monitor_plugins.load_all_parse_args(api_args)

    return monitor_plugins

@app.get("/networks")
async def networks():
    data = load_network_list()
    return data

@app.get("/networks/{network}")
async def network(network, status: bool = False, alerts: bool = False, seed: Optional[str] = Header(None)):
    monitor_plugins = set_plugin_parameters(status, alerts)
    network_info = init_network_args(network=network)

    ident = None
    if seed:
        try:
            ident = DidKey(seed)
            log("DID:", ident.did, " Verkey:", ident.verkey)
        except:
            log("Invalid seed.  Continuing anonymously ...")

    result = await fetch_status(monitor_plugins=monitor_plugins, genesis_path=network_info.genesis_path, ident=ident, network_name=network_info.network_name)
    return result

@app.get("/networks/{network}/{node}")
async def node(network, node, status: bool = False, alerts: bool = False, seed: Optional[str] = Header(None)):
    monitor_plugins = set_plugin_parameters(status, alerts)
    network_info = init_network_args(network=network)

    ident = None
    if seed:
        try:
            ident = DidKey(seed)
            log("DID:", ident.did, " Verkey:", ident.verkey)
        except:
            log("Invalid seed.  Continuing anonymously ...")

    result = await fetch_status(monitor_plugins, network_info.genesis_path, node, ident, network_info.network_name)
    return result