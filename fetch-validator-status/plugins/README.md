# Plug-ins

## Building Plug-ins

Build your own class based plugins to extract the information you want. Have a look at the included [example plug-in](Example/example.py) to see how to build your own. 

## About Plug-ins

Plug-in modals and packages are collected from the plug-ins folder and sorted based on the order specified by you by setting the index property in the given plug-in. Once the plug-ins are loaded the commmand line arguments are collected from the `parse_args()` function from each of the plug-ins. They are then passed into the `load_parse_args()` function where the plug-in collects its class variables.

The data collected from the network is passed in sequence to each of the plugins, giving each the opportunity to parse and manipulate the data before passing the result back for subsequent plugins.

note: plug-ins are only enabled when a flag is given. i.e. the [Alerts Plug-in](alerts/alerts.py) will only run if the `--alerts` flag is given. if you have a plug-in that requires more then one argument the first flag will enable the plug-in and the following flags would contain your additional arguments. See the [Network Metrics Plug-in](metrics/network_metrics.py) as an example.

Once the plug-ins are initialized, the monitor engine will collect the `validator-info` data from the nodes in the specified network. The engine will then pass the response to the [Analysis Plug-in](analysis.py) before passing the analyzed result to all of the subsequent plug-ins for processing.

Have a look at the included plug-ins to get an idea of how to build your own!

## Analysis

The [Analysis Plug-in](analysis.py) does an analysis of the response returned from the network; returns result.

*WARNING this plug-in has to run first in order for the other plug-ins to work. Plug-in index should be set to ZERO set inside the plug-in class under the INIT method. i.e. `self.index = 0`*
*This plug-in is required in order to run this monitor and will automatically run without a command line argument*

## Status Only Plug-in

The [Status Only Plug-in](status_only.py) removes response from the result returning only the status.

### How To Use
`./run.sh --net ssn --status` or `./run.sh --net ssn --status --alerts`

--status: enables the plug-in

### Example Print Out
```
[
  {
    "name": "Test",
    "client-address": "tcp://00.00.00.00:0000",
    "node-address": "tcp://00.00.00.00:0000",
    "status": {
      "ok": true,
      "timestamp": "1615837991"
    }
  },
  {
    "name": "ect",
    "client-address": "tcp://00.00.00.00:0000",
    "node-address": "tcp://00.00.00.00:0000",
    "status": {
      "ok": true,
      "timestamp": "1615837991"
    }
  }
]
```

## Network Metrics

See [readme](metrics/README.md)

## Alerts

See [readme](alerts/README.md)

## Generate Network Upgrade Schedule

See [readme](generate_upgrade_schedule/README.md)

## Example

See [readme](Example/README.md)
