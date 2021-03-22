# Example

The [Example Plug-in](example.py) is to be used as a template to build your own plug-ins. All is does is add `"examplePlugin": "Hello World"` to every response. This example is built as a package, but you can build plug-ins as a module like the Status Only Plug-in.   

Be sure to make a copy before you start building. 

## How To Use
`./run.sh --net ssn --status --example`

--example: enables the plug-in

## Example Print Out
```
[
  {
    "name": "test",
    "client-address": "tcp://00.000.000.000:0000",
    "node-address": "tcp://00.00.000.000:0000",
    "status": {
      "ok": true,
      "timestamp": "1615838114"
    },
    "examplePlugin": "Hello World"
  }
]
```