import plugin_collection
import json
import datetime
from DidKey import DidKey
from typing import Tuple

class main(plugin_collection.Plugin):

    def __init__(self):
        super().__init__()
        self.index = 0
        self.name = 'Analysis'
        self.description = ''
        self.type = ''
        self.enabled = True

    def parse_args(self, parser):
        pass

    def load_parse_args(self, args):
        global verbose
        verbose = args.verbose

    async def perform_operation(self, result, network_name, response, verifiers):
        primary = ""
        packages = {}
        for node, val in response.items():
            jsval = []
            status = {}
            errors = []
            warnings = []
            info = []
            entry = {"name": node}
            try:
                await self.get_node_addresses(entry, verifiers)
                jsval = json.loads(val)
                if not primary:
                    primary = await self.get_primary_name(jsval, node)
                errors, warnings = await self.detect_issues(jsval, node, primary)
                info = await self.get_info(jsval)
                packages[node] = await self.get_package_info(jsval)
            except json.JSONDecodeError:
                errors = [val]  # likely "timeout"

            # Status Summary
            entry["status"] = await self.get_status_summary(jsval, errors)
            # Info
            if len(info) > 0:
                entry["status"]["info"] = len(info)
                entry["info"] = info
            # Errors / Warnings
            if len(errors) > 0:
                entry["status"]["errors"] = len(errors)
                entry["errors"] = errors
            if len(warnings) > 0:
                entry["status"]["warnings"] = len(warnings)
                entry["warnings"] = warnings
            # Full Response
            if jsval:
                entry["response"] = jsval # put into status plugin minus response 

            result.append(entry)

            # Package Mismatches
            if packages:
                await self.merge_package_mismatch_info(result, packages)

            # Connection Issues
            await self.detect_connection_issues(result)

        return result

    async def get_node_addresses(self, entry: any, verifiers: any) -> any:
        if verifiers:
            node_name = entry["name"]
            if "client_addr" in verifiers[node_name]:
                entry["client-address"] = verifiers[node_name]["client_addr"]
            if "node_addr" in verifiers[node_name]:
                entry["node-address"] = verifiers[node_name]["node_addr"]

    async def get_primary_name(self, jsval: any, node: str) -> str:
        primary = ""
        if "REPLY" in jsval["op"]:
            if "Node_info" in jsval["result"]["data"]:
                primary = jsval["result"]["data"]["Node_info"]["Replicas_status"][node+":0"]["Primary"]
        return primary

    async def get_status_summary(self, jsval: any, errors: list) -> any:
        status = {}
        status["ok"] = (len(errors) <= 0)
        if jsval and ("REPLY" in jsval["op"]):
            if "Node_info" in jsval["result"]["data"]:
                status["uptime"] = str(datetime.timedelta(seconds = jsval["result"]["data"]["Node_info"]["Metrics"]["uptime"]))
            if "timestamp" in jsval["result"]["data"]:
                status["timestamp"] = jsval["result"]["data"]["timestamp"]
            else:
                status["timestamp"] = datetime.datetime.now().strftime('%s')
            if "Software" in jsval["result"]["data"]:
                status["software"] = {}
                status["software"]["indy-node"] = jsval["result"]["data"]["Software"]["indy-node"]
                status["software"]["sovrin"] = jsval["result"]["data"]["Software"]["sovrin"]

        return status

    async def get_package_info(self, jsval: any) -> any:
        packages = {}
        if jsval and ("REPLY" in jsval["op"]):
            if "Software" in jsval["result"]["data"]:
                for installed_package in jsval["result"]["data"]["Software"]["Installed_packages"]:
                    package, version = installed_package.split()
                    packages[package] = version

        return packages

    async def get_info(self, jsval: any) -> any:
        info = []
        if ("REPLY" in jsval["op"]) and ("Extractions" in jsval["result"]["data"]):
            # Pending Upgrade
            if jsval["result"]["data"]["Extractions"]["upgrade_log"]:
                current_upgrade_status = jsval["result"]["data"]["Extractions"]["upgrade_log"][-1]
                if "succeeded" not in current_upgrade_status:
                    info.append("Pending Upgrade: {0}".format(current_upgrade_status.replace('\t', '  ').replace('\n', '')))

        return info

    async def merge_package_mismatch_info(self, result: any, packages: any):
        package_warnings = await self.check_package_versions(packages)
        if package_warnings:
            for node_name in package_warnings:
                entry_to_update = [t for t in result if t["name"] == node_name][0]
                if "warnings" in entry_to_update:
                    for item in package_warnings[node_name]:
                        entry_to_update["warnings"].append(item)
                else:
                    entry_to_update["warnings"] = package_warnings[node_name]
                entry_to_update["status"]["warnings"] = len(entry_to_update["warnings"])

    async def check_package_versions(self, packages: any) -> any:
        warnings = {}
        for node, package_list in packages.items():
            mismatches = []
            for package, version in package_list.items():
                total = 0
                same = 0
                other_version = ""
                for comp_node, comp_package_list in packages.items():
                    if package in comp_package_list:
                        total +=1
                        comp_version = comp_package_list[package]
                        if comp_version == version:
                            same +=1
                        else:
                            other_version = comp_version
                if (same/total) < .5:
                    mismatches.append("Package mismatch: '{0}' has '{1}' {2}, while most other nodes have '{1}' {3}".format(node, package, version, other_version))
            if mismatches:
                warnings[node] = mismatches
        return warnings

    async def detect_issues(self, jsval: any, node: str, primary: str) -> Tuple[any, any]:
        errors = []
        warnings = []
        ledger_sync_status={}
        if "REPLY" in jsval["op"]:
            if "Node_info" in jsval["result"]["data"]:
                # Ledger Write Consensus Issues
                if not jsval["result"]["data"]["Node_info"]["Freshness_status"]["0"]["Has_write_consensus"]:
                    errors.append("Config Ledger Has_write_consensus: {0}".format(jsval["result"]["data"]["Node_info"]["Freshness_status"]["0"]["Has_write_consensus"]))
                if not jsval["result"]["data"]["Node_info"]["Freshness_status"]["1"]["Has_write_consensus"]:
                    errors.append("Main Ledger Has_write_consensus: {0}".format(jsval["result"]["data"]["Node_info"]["Freshness_status"]["1"]["Has_write_consensus"]))
                if not jsval["result"]["data"]["Node_info"]["Freshness_status"]["2"]["Has_write_consensus"]:
                    errors.append("Pool Ledger Has_write_consensus: {0}".format(jsval["result"]["data"]["Node_info"]["Freshness_status"]["2"]["Has_write_consensus"]))
                if "1001" in  jsval["result"]["data"]["Node_info"]["Freshness_status"]:
                    if not jsval["result"]["data"]["Node_info"]["Freshness_status"]["1001"]["Has_write_consensus"]:
                        errors.append("Token Ledger Has_write_consensus: {0}".format(jsval["result"]["data"]["Node_info"]["Freshness_status"]["1001"]["Has_write_consensus"]))

                # Ledger Status
                for ledger, status in jsval["result"]["data"]["Node_info"]["Catchup_status"]["Ledger_statuses"].items():
                    if status != "synced":
                        ledger_sync_status[ledger] = status
                if ledger_sync_status:
                    ledger_status = {}
                    ledger_status["ledger_status"] = ledger_sync_status
                    ledger_status["ledger_status"]["transaction-count"] = jsval["result"]["data"]["Node_info"]["Metrics"]["transaction-count"]
                    warnings.append(ledger_status)

                # Mode
                if jsval["result"]["data"]["Node_info"]["Mode"] != "participating":
                    warnings.append("Mode: {0}".format(jsval["result"]["data"]["Node_info"]["Mode"]))

                # Primary Node Mismatch
                if jsval["result"]["data"]["Node_info"]["Replicas_status"][node+":0"]["Primary"] != primary:
                    warnings.append("Primary Mismatch! This Nodes Primary: {0} (Expected: {1})".format(jsval["result"]["data"]["Node_info"]["Replicas_status"][node+":0"]["Primary"], primary))

                # Unreachable Nodes
                if jsval["result"]["data"]["Pool_info"]["Unreachable_nodes_count"] > 0:
                    unreachable_node_list = []
                    unreachable_nodes = {"unreachable_nodes":{}}
                    unreachable_nodes["unreachable_nodes"]["count"] = jsval["result"]["data"]["Pool_info"]["Unreachable_nodes_count"]
                    for unreachable_node in jsval["result"]["data"]["Pool_info"]["Unreachable_nodes"]:
                        unreachable_node_list.append(unreachable_node[0])
                    unreachable_nodes["unreachable_nodes"]["nodes"] = ', '.join(unreachable_node_list)
                    warnings.append(unreachable_nodes)

                # Denylisted Nodes
                if len(jsval["result"]["data"]["Pool_info"]["Blacklisted_nodes"]) > 0:
                    warnings.append("Denylisted Nodes: {1}".format(jsval["result"]["data"]["Pool_info"]["Blacklisted_nodes"]))
        else:
            if "reason" in jsval:
                errors.append(jsval["reason"])
            else:
                errors.append("unknown error")

        return errors, warnings

    async def detect_connection_issues(self, result: any) -> any:
        for node in result:
            connection_errors = []
            node_name = node["name"]
            if "warnings" in node:
                for warning in node["warnings"]:
                    if "unreachable_nodes" in warning :
                        for item in warning["unreachable_nodes"]["nodes"].split(', '):
                            # This is the name of the unreachable node.  Now we need to determine whether that node can't see the current one.
                            # If the nodes can't see each other, upgrade to an error condition.
                            unreachable_node_name = item
                            unreachable_node_query_result = [t for t in result if t["name"] == unreachable_node_name]
                            if unreachable_node_query_result:
                                unreachable_node = unreachable_node_query_result[0]
                                if "warnings" in unreachable_node:
                                    for unreachable_node_warning in unreachable_node["warnings"]:
                                        if "unreachable_nodes" in unreachable_node_warning :
                                            for unreachable_node_item in unreachable_node_warning["unreachable_nodes"]["nodes"].split(', '):
                                                if unreachable_node_item == node_name:
                                                    connection_errors.append(node_name + " and " + unreachable_node_name + " can't reach each other.")

            # Merge errors and update status
            if connection_errors:
                if "errors" in node:
                    for item in connection_errors:
                        node["errors"].append(item)
                else:
                    node["errors"] = connection_errors
                node["status"]["errors"] = len(node["errors"])
                node["status"]["ok"] = (len(node["errors"]) <= 0)