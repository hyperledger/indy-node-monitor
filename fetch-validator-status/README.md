# Fetch Validator Status

This folder contains a simple Python script that uses [indy-vdr](https://github.com/hyperledger/indy-vdr) to execute a "validator-info" call to an Indy network. The validator info transaction script returns a great deal of information about the accessed ledger. An example of the JSON data returned by the call for an individual node is provided [below](#example-validator-info).

The call can only be made by an entity with a suitably authorized DID on the ledger. For example, on the Sovrin MainNet, only Stewards and some within the Sovrin Foundation has that access.

The easiest way to use this now is to use the `./run` script and the Docker build process provide in this folder. Work is in progress to add a CI/CD capability to `indy-vdr` so that the artifacts are published to PyPi and native Python apps can be used. In the meantime, we recommend building your own [plug-in](plugins/README.md).

## How To Run

Here is guidance of how you can run the script to get validator info about any accessible Indy network. We'll start with a test on local network (using [von-network](https://github.com/bcgov/von-network)) and provide how this can be run on any Indy network, including Sovrin networks.

### Prerequisites

If you are running locally, you must have `git`, `docker` and a bash terminal. On Windows, when you install `git`, the `git-bash` terminal is installed and you can use that.

To try this in a browser, go to [Play With Docker](https://labs.play-with-docker.com/), login (requires a Docker Hub ID) and click the "+ ADD NEW INSTANCE` link (left side). That opens a terminal session that you can use to run these steps.

The rest of the steps assume you are in your bash terminal in a folder where GitHub repos can be cloned.

### Start VON Network

To start a local Indy network to test with, we'll clone a VON Network, build it and start it using the following commands run in a bash terminal:

``` bash
git clone https://github.com/bcgov/von-network
cd von-network
./manage build
./manage start
cd ..

```

The build step will take a while as 1/3 of the Internet is downloaded. Eventually, the `start` step will execute and a four-node Indy ledger will start.  Wait about 30 seconds and then go to the web interface to view the network.

- If you are running locally, go to [http://localhost:9000](http://localhost:9000).
- If you are on Play with Docker, click the `9000` link above the terminal session window.

Note the last command above puts you back up to the folder in which you started. If you want to explore `von-network` you'll have to change back into the `von-network` folder.

When you are finished your running the validator tool (covered in the steps below) and want to stop your local indy-network, change to the von-network folder and run:

```bash
./manage down

```

We'll remind you of that later in these instructions.

### Clone the indy-node-monitor repo

Run these commands to clone this repo so that you can run the fetch validator info command.

```bash
git clone https://github.com/bcgov/indy-node-monitor
cd indy-node-monitor/fetch-validator-status

```

### Run the Validator Info Script

For a full list of script options run:
``` bash
./run.sh -h
```

To get the details for the known networks available for use with the `--net` option, run:
``` bash
./run.sh --list-nets
```

To run the validator script, run the following command in your bash terminal from the `fetch-validator-status` folder in the `indy-node-monitor` clone:

``` bash
./run.sh --net=<netId> --seed=<SEED>
```
or
``` bash
./run.sh --genesis-url=<URL> --seed=<SEED>
```

To just get a status summary for the nodes, run:
``` bash
./run.sh --net=<netId> --seed=<SEED> --status
```
or
``` bash
./run.sh --genesis-url=<URL> --seed=<SEED> --status
```

To fetch data for a single node, or a particular set of nodes use the `--nodes` argument and provide a comma delimited list of node names (aliases);
``` bash
./run.sh --net=<netId> --seed=<SEED> --status --nodes node1,node2
```

For the first test run using von-network:

- the `<SEED>` is the Indy test network Trustee seed: `000000000000000000000000Trustee1`.
- the URL is retrieved by clicking on the `Genesis Transaction` link in the VON-Network web interface and copying the URL from the browser address bar.

If you are running locally, the full command is:

``` bash
./run.sh --net=vn --seed=000000000000000000000000Trustee1
```
or
``` bash
./run.sh --genesis-url=http://localhost:9000/genesis --seed=000000000000000000000000Trustee1
```

To perform an anonymous connection test when a privileged DID seed is not available, omit the `SEED` (`-a` is no longer needed to perform an anonymous connection):

``` bash
./run.sh --net=<netId>
```
or
``` bash
./run.sh --genesis-url=<URL>
```

If running in the browser, you will have to get the URL for the Genesis file (as described above) and replace the `localhost` URL above.

You should see a very long JSON structure printed to the terminal. You can redirect the output to a file by adding something like `> good.json` at the end of the command.

If you use the Seed of a DID that does not have permission to see validator info, you will get a much shorter JSON structure containing access denied messages.

### Damage the Indy Network

To see what happens when a node is terminated, or inaccessible, terminate one of the von-network nodes and then re-run the validator info script. To terminate a von-network node run:

``` bash
docker kill von_node1_1
```

When you repeat the run, you'll see that:

- the command takes a while to run as it waits for a timeout from the terminated node
- the entry from the terminate node is empty (but still present)
- the entries of the other nodes indicate that the terminated node is not accessible

Try redirecting the output to `>bad.json` and then use `diff good.json bad.json` to see all the differences. Better yet a visual diff tool.

If you are finished trying this out with a local Indy network, don't forget to go back and shutdown the instance of von-network, using the commands:

``` bash
cd ../..
cd von-network
./manage down

```

### Extracting Useful Information

Once you have the script running, you can write a plug-in that takes the JSON input and produces a more useful monitoring output file&mdash;probably still in JSON. Here is some information that would be useful to extract from the JSON output:

- Detect when a node is inaccessible (as with Node 1 above) and produce standard output for that situation.
- Detect any nodes that are accessible (populated JSON data) but that are "unreachable" to some or all of the other Indy nodes.
  - That indicates that the internal port to the node is not accessible, even though the public port is accessible.
- The number of transaction per Indy ledger, especially the domain ledger.
- The average read and write times for the node.
- The average throughput time for the node.
- The uptime of the node (time is last restart).
- The time since last freshness check (should be less than 5 minutes).

The suggestions above are only ideas. Precise meanings of the values should be investigated, particularly for "ledger" type data (e.g. number of transactions) but that are generated on a per node basis.

Note that there are three different formats for the timestamps in the data structure, and all appear to be UTC. Make sure to convert times into a single format during collection.


## Plug-ins

For info on plug-ins see the plug-ins [readme](plugins/README.md)

## Rest API

For info on Rest API see [REST API](REST_API.md)

### Running against other Indy Networks

To see the validator info against any other Indy network, you need a URL for the Genesis file for the network, and the seed for a suitably authorized DID. The pool Genesis file URLs are easy, since that is published data needed by agents connecting to Indy networks. Sovrin genesis URLs can be found [here](https://github.com/sovrin-foundation/sovrin/tree/master/sovrin). You need the URL for the raw version of the pool transaction files. For example, the URL you need for the Sovrin MainNet is:

- [`https://raw.githubusercontent.com/sovrin-foundation/sovrin/master/sovrin/pool_transactions_live_genesis`](`https://raw.githubusercontent.com/sovrin-foundation/sovrin/master/sovrin/pool_transactions_live_genesis`)

For the other Sovrin networks, replace `live` with `sandbox` (Sovrin Staging Net) and `builder` (Sovrin Builder Net).

Getting a Seed for a DID with sufficient authorization on specific ledger is an exercise for the user. **DO NOT SHARE DID SEEDS**. Those are to be kept secret.

Do not write the Seeds in a public form. The use of environment variables for these parameters is very deliberate so that no one accidentally leaks an authorized DID.

Did I mention: **DO NOT SHARE DID SEEDS**?

## Example Validator info

The following is an example of the data for a single node from a VON-Network instance:

```JSONC
[
  {
    "name": "Node4",
    "response": {
      "response-version": "0.0.1",
      "timestamp": 1594079906,
      "Hardware": {
        "HDD_used_by_node": "2 MBs"
      },
      "Pool_info": {
        "Read_only": false,
        "Total_nodes_count": 4,
        "f_value": 1,
        "Quorums": "{'n': 4, 'f': 1, 'weak': Quorum(2), 'strong': Quorum(3), 'propagate': Quorum(2), 'prepare': Quorum(2), 'commit': Quorum(3), 'reply': Quorum(2), 'view_change': Quorum(3), 'election': Quorum(3), 'view_change_ack': Quorum(2), 'view_change_done': Quorum(3), 'same_consistency_proof': Quorum(2), 'consistency_proof': Quorum(2), 'ledger_status': Quorum(2), 'ledger_status_last_3PC': Quorum(2), 'checkpoint': Quorum(2), 'timestamp': Quorum(2), 'bls_signatures': Quorum(3), 'observer_data': Quorum(2), 'backup_instance_faulty': Quorum(2)}",
        "Reachable_nodes": [
        [
          "Node1",
          0
        ],
        [
          "Node3",
          null
        ],
        [
          "Node4",
          null
        ]
        ],
        "Unreachable_nodes": [
        [
          "Node2",
          null
        ]
        ],
        "Reachable_nodes_count": 3,
        "Unreachable_nodes_count": 1,
        "Blacklisted_nodes": [],
        "Suspicious_nodes": ""
      },
      "Protocol": {},
      "Node_info": {
        "Name": "Node4",
        "Mode": "participating",
        "Client_port": 9708,
        "Client_ip": "0.0.0.0",
        "Client_protocol": "tcp",
        "Node_port": 9707,
        "Node_ip": "0.0.0.0",
        "Node_protocol": "tcp",
        "did": "4PS3EDQ3dW1tci1Bp6543CfuuebjFrg36kLAUcskGfaA",
        "verkey": "68yVKe5AeXynD5A8K91aTZFjCQEoKV4hKPtauqjHa9phgitWEGkS5TR",
        "BLS_key": "2zN3bHM1m4rLz54MJHYSwvqzPchYp8jkHswveCLAEJVcX6Mm1wHQD1SkPYMzUDTZvWvhuE6VNAkK3KxVeEmsanSmvjVkReDeBEMxeDaayjcZjFGPydyey1qxBHmTvAnBKoPydvuTAqx5f7YNNRAdeLmUi99gERUU7TD8KfAa6MpQ9bw",
        "Metrics": {
        "Delta": 0.1,
        "Lambda": 240,
        "Omega": 20,
        "instances started": {
          "0": 252658.103411107
        },
        "ordered request counts": {
          "0": 16
        },
        "ordered request durations": {
          "0": 11.218815947
        },
        "max master request latencies": 0,
        "client avg request latencies": {
          "0": null
        },
        "throughput": {
          "0": 0.0017547843
        },
        "master throughput": 0.0017547843,
        "total requests": 16,
        "avg backup throughput": null,
        "master throughput ratio": null,
        "average-per-second": {
          "read-transactions": 0.0338584473,
          "write-transactions": 0.0001539895
        },
        "transaction-count": {
          "ledger": 21,
          "pool": 4,
          "config": 0,
          "audit": 1042
        },
        "uptime": 103903
        },
        "Committed_ledger_root_hashes": {
        "3": "b'C3ofBGxtL6xAWXtSFcGPamSnHqT1hB2MckzPXYpy7q7e'",
        "0": "b'EE9Dr84v87WGqiDFhHYHC9eVF1f1q3E8GnkXNbuZ7D8y'",
        "2": "b'GKot5hBsd81kMupNCXHaqbhv3huEbxAFMLnpcX2hniwn'",
        "1": "b'45YwJVR1Lzb5u5zGAetkbBXY2YdLixvc5j2eSz2vyQgn'"
        },
        "Committed_state_root_hashes": {
        "2": "b'DfNLmH4DAHTKv63YPFJzuRdeEtVwF5RtVnvKYHd8iLEA'",
        "0": "b'8xwEHCkVcEA9qfBJaESpWKvtHVxUkvzJctAHfBiVhAAJ'",
        "1": "b'EozN1ekxkmMRGMeBNoBWTYi47PCZTP2vTgNN5GKgto1H'"
        },
        "Uncommitted_ledger_root_hashes": {},
        "Uncommitted_ledger_txns": {
        "3": {
          "Count": 0
        },
        "0": {
          "Count": 0
        },
        "2": {
          "Count": 0
        },
        "1": {
          "Count": 0
        }
        },
        "Uncommitted_state_root_hashes": {
        "2": "b'DfNLmH4DAHTKv63YPFJzuRdeEtVwF5RtVnvKYHd8iLEA'",
        "0": "b'8xwEHCkVcEA9qfBJaESpWKvtHVxUkvzJctAHfBiVhAAJ'",
        "1": "b'EozN1ekxkmMRGMeBNoBWTYi47PCZTP2vTgNN5GKgto1H'"
        },
        "View_change_status": {
        "View_No": 0,
        "VC_in_progress": false,
        "Last_view_change_started_at": "1970-01-01 00:00:00",
        "Last_complete_view_no": 0,
        "IC_queue": {},
        "VCDone_queue": {}
        },
        "Catchup_status": {
        "Ledger_statuses": {
          "3": "synced",
          "0": "synced",
          "2": "synced",
          "1": "synced"
        },
        "Received_LedgerStatus": "",
        "Waiting_consistency_proof_msgs": {
          "3": null,
          "0": null,
          "2": null,
          "1": null
        },
        "Number_txns_in_catchup": {
          "3": 0,
          "0": 0,
          "2": 0,
          "1": 0
        },
        "Last_txn_3PC_keys": {
          "3": {
          "Node2": [
            null,
            null
          ],
          "Node3": [
            null,
            null
          ]
          },
          "0": {
          "Node3": [
            null,
            null
          ],
          "Node2": [
            null,
            null
          ]
          },
          "2": {
          "Node2": [
            null,
            null
          ],
          "Node3": [
            null,
            null
          ]
          },
          "1": {
          "Node3": [
            null,
            null
          ],
          "Node2": [
            null,
            null
          ]
          }
        }
        },
        "Freshness_status": {
        "1": {
          "Last_updated_time": "2020-07-06 23:55:07+00:00",
          "Has_write_consensus": true
        },
        "0": {
          "Last_updated_time": "2020-07-06 23:57:33+00:00",
          "Has_write_consensus": true
        },
        "2": {
          "Last_updated_time": "2020-07-06 23:57:33+00:00",
          "Has_write_consensus": true
        }
        },
        "Requests_timeouts": {
        "Propagates_phase_req_timeouts": 0,
        "Ordering_phase_req_timeouts": 0
        },
        "Count_of_replicas": 1,
        "Replicas_status": {
        "Node4:0": {
          "Primary": "Node1:0",
          "Watermarks": "1000:1300",
          "Last_ordered_3PC": [
          0,
          1042
          ],
          "Stashed_txns": {
          "Stashed_checkpoints": 0,
          "Stashed_PrePrepare": 0
          }
        }
        }
      },
      "Software": {
        "OS_version": "Linux-4.15.0-109-generic-x86_64-with-debian-buster-sid",
        "Installed_packages": [
        "zipp 2.2.0",
        "yarl 1.4.2",
        "wcwidth 0.1.8",
        "ujson 1.33",
        "typing 3.7.4.1",
        "typing-extensions 3.7.4.1",
        "timeout-decorator 0.4.0",
        "supervisor 4.0.4",
        "sortedcontainers 1.5.7",
        "six 1.11.0",
        "sha3 0.2.1",
        "setuptools 40.6.2",
        "semver 2.7.9",
        "rlp 0.6.0",
        "pyzmq 18.1.0",
        "PyYAML 5.1.2",
        "python3-indy 1.14.1",
        "python-rocksdb 0.6.9",
        "python-dateutil 2.6.1",
        "pytest 5.3.5",
        "pyparsing 2.4.6",
        "Pympler 0.5",
        "Pygments 2.2.0",
        "pycparser 2.19",
        "pycares 3.1.1",
        "py 1.8.1",
        "psutil 5.4.3",
        "prompt-toolkit 0.57",
        "portalocker 0.5.7",
        "pluggy 0.13.1",
        "pip 9.0.3",
        "packaging 19.0",
        "orderedset 2.0",
        "multidict 4.7.4",
        "msgpack-python 0.4.6",
        "more-itertools 8.2.0",
        "meld3 2.0.1",
        "MarkupSafe 1.1.1",
        "libnacl 1.6.1",
        "leveldb 0.201",
        "jsonpickle 0.9.6",
        "Jinja2 2.11.2",
        "ioflo 1.5.4",
        "intervaltree 2.1.0",
        "indy-plenum 1.12.2",
        "indy-node 1.12.2",
        "importlib-metadata 1.5.0",
        "idna 2.8",
        "idna-ssl 1.1.0",
        "distro 1.3.0",
        "chardet 3.0.4",
        "cffi 1.14.0",
        "cchardet 2.1.5",
        "base58 1.0.3",
        "attrs 19.3.0",
        "async-timeout 3.0.1",
        "aiosqlite 0.10.0",
        "aiohttp 3.5.4",
        "aiohttp-jinja2 1.1.2",
        "aiodns 2.0.0",
        "indy-crypto 0.5.1"
        ],
        "Indy_packages": [
        ""
        ],
        "indy-node": "1.12.2",
        "sovrin": "unknown"
      },
      "Update_time": "Monday, July 6, 2020 11:58:26 PM +0000",
      "Memory_profiler": [],
      "Extractions": {
        "journalctl_exceptions": [
        ""
        ],
        "indy-node_status": [
        ""
        ],
        "node-control status": [
        ""
        ],
        "upgrade_log": "",
        "stops_stat": null
      }
    }
  }
]
```
