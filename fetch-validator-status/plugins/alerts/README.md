# Alerts

The [Alerts Plug-in](alerts.py) filters out nodes that contain "info", "warnings", or "errors" in the "status" field. Can by used in conjuction with the Status Only Plug-in.

## How To Use
`./run.sh --net ssn --alerts` or `./run.sh --net ssn --alerts --status `

--alerts: enables the plug-in

## Example Print Out
```
[
  {
    "name": "test",
    "client-address": "tcp://00.000.000.000:0000",
    "node-address": "tcp://00.00.000.000:0000",
    "status": {
      "ok": False,
      "timestamp": "1615838114",
      'errors': 1
    },
    'errors': ['timeout']
  }
]
```