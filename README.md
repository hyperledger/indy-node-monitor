# Indy Node Monitor

Indy Node Monitor is a set of tools for monitoring the status of an Indy Ledger by querying the validator information of the nodes of the ledger. Based on that, data can be generated data suitable for:

* visualization on a dashboard
* tracking trends about the status of nodes and the overall ledger
* tracking read and write uptimes
* tracking ledger usage such as number of transactions on the ledger
* driving notifications of node outages

The repo has basic tools to collect and format data and tools for using that data in different ways.

Contributions are welcome of tools that consume the collected data to enable easy ways to monitor an Indy network, such as configurations of visualization dashboards that can be deployed by many users. For example, an ELK stack or Splunk configuration that receives validator info and presents it in a ledger dashboard. Or an interface to [Pager Duty](https://www.pagerduty.com/) to enable node outage notifications.

## Fetch Validator Status

This is a simple tool that can be used to retrieve "validator-info"&mdash;detailed status data about an Indy node (aka "validator)&mdash;from all the nodes in a network. The results are returned as a JSON array with a record per validator.

For more details see the Fetch Validator Status [readme](fetch-validator-status/README.md)

## Project Structure

Where ever possible, all processes and solutions should be containerized.  This helps manage dependency issues and makes it easy to spin up the tools and dashboards locally or in a hosted container platform.

The core elements of the project are contained in the [fetch-validator-status](./fetch-validator-status) directory.  As described above this is the starting point for collecting data for monitoring the nodes on a given network.  The underlying script is itself wrapped in a container to make it easy to run.  However that does not preclude incorporating the script directly in a another solution.

Components, exporters in particular, should be developed using IOC (plug-in) patterns to allow micro-services, exporters, and dashboards to be mixed and matched as appropriate to allow end-to-end monitoring solutions to be more easily provisioned and maintained.

Solutions should adhere to the following directory structure:

```
docker/                     - Top level directory to contain all Dockerfiles
└── <micro_service_name>      - Directory containing the Dockerfile and supporting files for a specific micro-service.
                                The name should describe the micro-service's functionality not it's tech stack.
                                Names of any sub-directories are up to the author.

exporters/                  - Top level directory to contain all exporter implementations
└── <exporter_name>           - Directory containing a specific exporter implementation.
                                The name should describe the intended target, Prometheus for example.
                                Names of any sub-directories are up to the author.

dashboards/                 - Top level directory to contain all dashboard implementations
└── <dashboard_name>          - Directory containing a specific dashboard implementation.
                                The name should describe the application for which the dashboard was intended, Grafana for example.
                                Names of any sub-directories are up to the author.
```

## Contributions

Pull requests are welcome! Please read our [contributions guide](CONTRIBUTING.md) and submit your PRs. We enforce developer certificate of origin (DCO) commit signing. See guidance [here](https://github.com/apps/dco).

We also welcome issues submitted about problems you encounter in using the tools within this repo.

## Code of Conduct

All contributors are required to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md) guidelines.

## License

[Apache License Version 2.0](LICENSE)