# Indy Node Monitor
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Lifecycle:Maturing](https://img.shields.io/badge/Lifecycle-Maturing-007EC6)](https://github.com/bcgov/repomountie/blob/master/doc/lifecycle-badges.md)

Indy Node Monitor is a set of tools for monitoring the status of an Indy Ledger by querying the validator information of the nodes on the ledger.  These tools are integrated into a full monitoring stack including the following components:

- Indy Node Monitor (Fetch Validator Status)
- Telegraf
- Prometheus and/or InfluxDB
- Alert Manager
- Grafana

This allows you to:
- Visualize the node and network data on dashboards.
- Track trends about the status of nodes and the overall ledger.
- Track read and write uptimes.
- Tracking ledger usage such as number of transactions on the ledger.
- Drive notifications of node outages.

The stack is easily managed and spun up in docker using the included `./manage` script. Starting the stack is as easy as:
```
./manage build
./manage start
```

A browser window to the Grafana instance should launch automatically.  The login username is `admin` and the password `foobar`.  Once logged in you are able to browse the various (auto-provisioned) dashboards which will begin to populate after a few minutes.  *Please note:- In order to collect detailed data from the network to populate many of the graphs you will require a privileged DID (NETWORK_MONITOR at minimum) on the ledger and you will need to configure the monitoring stack with the seed(s).*

For more information about the commands available in the `./manage` script refer to the [command list](docs/README.md#command-list)

For more infomration on how to setup and use the monitoring stack refer to this [readme](docs/README.md#setting-up-the-monitoring-stack)

## Fetch Validator Status

This simple tool is the heart of the Indy Node Monitor.  It is used to retrieve "validator-info"&mdash;detailed status data about an Indy node (aka "validator")&mdash;from all the nodes in a network. The results are returned as a JSON array with a record per validator, and the data can be manipulated and formatted through the use of plugins.  Fetch validator status can be used as a stand-alone command line tool or through the Indy Node Monitor REST API which is used by the monitoring stack.  The Indy Node Monitor REST API can be spun up easily by running `./manage start indy-node-monitor`, and a browser window will automatically launch to display the API documents and interface.

For more details see the Fetch Validator Status [readme](fetch-validator-status/README.md)

## How to contribute to the monitoring stack

For more details on how to contribute follow the link to this [readme](docs/README.md)

## Contributions

Pull requests are welcome! Please read our [contributions guide](CONTRIBUTING.md) and submit your PRs. We enforce developer certificate of origin (DCO) commit signing. See guidance [here](https://github.com/apps/dco).

We also welcome issues submitted about problems you encounter in using the tools within this repo.

## Code of Conduct

All contributors are required to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md) guidelines.

## License

[Apache License Version 2.0](LICENSE)