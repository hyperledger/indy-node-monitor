#!/usr/bin/env python3
import argparse
import subprocess
import json
import sys
import re
import time
import os

label = "indy_node"
def filter_timestamps(data):
    filtered=[]
    for l in data.splitlines():
        if re.match(r'^[0-9]{4}-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-6][0-9]:[0-6][0-9],[0-9]+ .*',l):
            continue              
        filtered.append(l)
    return ''.join(filtered)

def flatten_dict(d,separator='.',parent_key=''):
    items=[]
    try:
        d_items = d.items()
    except AttributeError:
        i=0
        for e in d:
            new_key = '{}'.format(i)
            if isinstance(e,str):
                items.append((new_key,e))
            elif isinstance(e,float):
                items.append((new_key,e))
            elif isinstance(e,int):
                items.append((new_key,e))
            else:
                items.extend(
                    flatten_dict(e,separator=separator,parent_key=new_key).items()
                )
            i+=1
        return dict(items)
    for k, v in d.items():
        if parent_key:
            new_key = '{}{}{}'.format(parent_key,separator,k)
        else:
            new_key = k
        if isinstance(v,dict):
            items.extend(
                flatten_dict(v,separator=separator,parent_key=new_key).items()
            )
        elif isinstance(v,list):
            org_key=new_key
            i=0
            for e in v:
                new_key = '{}{}{}'.format(org_key,separator,i)
                if isinstance(e,str):
                    items.append((new_key,e))
                elif isinstance(e,float):#.split('{',1)[1]))
                    items.append((new_key,e))
                elif isinstance(e,int):
                    items.append((new_key,e))
                else:
                    items.extend(
                        flatten_dict(e,separator=separator,parent_key=new_key).items()
                    )
                i+=1
        else:
            items.append((new_key,v))
    return dict(items)

def _get_metrics_live(GENESIS_URL, SEED):
    try:
        my_env = os.environ.copy()
        my_env["GENESIS_URL"] =  GENESIS_URL
        my_env["SEED"] = SEED  
        proc = subprocess.Popen(["/home/ubuntu/github/indy-node-monitor/fetch-validator-status/run.sh"],env=my_env,cwd=r'/home/ubuntu/github/indy-node-monitor/fetch-validator-status',stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        ret = proc.communicate(timeout=100)
        if proc.returncode != 0:
            sys.stderr.write("ERROR occured running validator command\n")
            sys.stderr.write("STDOUT:\n")
            sys.stderr.write(ret[0].decode())
            sys.stderr.write("STERR:\n")
            sys.stderr.write(ret[1].decode())
        else:
            #Load Json
            return json.loads(filter_timestamps(ret[0].decode().replace("\r\n","")))
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        exc_str = "{}: {}".format(exc_type.__name__,exc_value)
        sys.stderr.write("Error executing validator-info: '{exc_str}'\n".format(exc_str=exc_str))
        sys.stderr.write("validator-info output: {}".format(ret[0].decode().replace("\r\n","").split('{',1)[1]))
        return None

def _process_1_5():
    node_info = data['Node_info']
    node_name = node_info['Name']
    metrics = node_info['Metrics']
    pool_metrics = data['Pool_info']
    version_metrics = data['Software']
    #Process Pool related metrics
    for metric in pool_metrics:
        # If it is a "count" metric, assume that the value is a number and good to go
        if 'count' in metric:
            try:
                float(pool_metrics[metric])
                val = pool_metrics[metric]
                print('indy_{metric}{{node_name="{node_name}",source="{label}"}} {value}'.format(
                        metric=metric.replace('-','_').replace(' ','_').lower(),
                        node_name=node_name,
                        label=label,
                        value=val
                    )
                )
            except ValueError:
                sys.stderr.write("Skipping unknown pool metric: '{}'\n".format(metric))
            continue
        # If it is a reachable nodes one, then is probably a list and process these two metrics
        if metric.lower() in [ 'unreachable_nodes','reachable_nodes' ]:
            if metric.lower() == 'reachable_nodes':
                val = 1
            else:
                val = 0
            for node in pool_metrics[metric]:
                if isinstance(node,list):
                    node_real = node[0]
                else:
                    node_real = node
                print('indy_reachable{{node="{node}",node_name="{node_name}",source="{label}"}} {value}'.format(
                        node=node_real,
                        node_name=node_name,
                        label=label,
                        value=val
                    )
                )
                if 0 == node[1]: 
                    print('indy_primary_node{{node="{node}",node_name="{node_name}",source="{label}"}} {value}'.format(
                            node=node_real,
                            node_name=node_name,
                            label=label,
                            value=0
                        )
                    )
            continue
    #Print version metrics directly
    print('indy_sovrin_version{{version="{version}",node_name="{node_name}",source="{label}"}} {value}'.format(
            version=version_metrics['sovrin'],
            node_name=node_name,
            label=label,
            value=0
        )
    )
    print('indy_node_version{{version="{version}",node_name="{node_name}",source="{label}"}} {value}'.format(
            version=version_metrics['indy-node'],
            node_name=node_name,
            label=label,
            value=0
        )
    )

    #Print timestamp metric directly
    print('indy_node_current_timestamp{{node_name="{node_name}",source="{label}"}} {value}'.format(
            node_name=node_name,
            label=label,
            value=data['timestamp']*1000
        )
    )

    #Process general Metrics
    for metric in metrics:
        try:
            metric_obj = metrics[metric]
            # If it is a dictionary, go one level deep and check if it is a value
            if isinstance(metric_obj,dict):
                for name in metric_obj:
                    # See if the value is a number and use it
                    try:
                        val = float(metric_obj[name])
                        print('indy_{metric}{{node_name="{node_name}",source="{label}",ident="{ident}"}} {value}'.format(
                                metric=metric.replace('-','_').replace(' ','_').lower(),
                                node_name=node_name,
                                label=label,
                                ident=name.replace('-','_').replace(' ','_').lower(),
                                value=val
                            )
                        )
                    # Must not be a number, flatten the object (works for a List or a Dict), then make
                    # some guesses about what the metric name should be, and a "name" for future filtering
                    except TypeError:
                        flat_d = flatten_dict(metric_obj,'|')
                        for name_key in flat_d:
                            val = float(flat_d[name_key])
                            name_split = name_key.split('|')
                            name = name_split[-1]
                            key = '_'.join(name_split[:-1])
                            print('indy_{metric}_{key}{{name="{name}",node_name="{node_name}",source="{label}"}} {value}'.format(
                                    metric=metric.replace('-','_').replace(' ','_').lower(),
                                    key=key,
                                    name=name,
                                    node_name=node_name,
                                    label=label,
                                    value=val
                                )
                            )
            # If is a list, flatten it and use the index number as a label for future filtering.
            elif isinstance(metric_obj,list):
                flat_d = flatten_dict(metric_obj)
                for idx in flat_d:
                    val = float(flat_d[idx])
                    print('indy_{metric}{{index="{idx}",node_name="{node_name}",source="{label}"}} {value}'.format(
                            metric=metric.replace('-','_').replace(' ','_').lower(),
                            idx=idx,
                            node_name=node_name,
                            label=label,
                            value=val
                        )
                    )
            else:
                raise TypeError
        # This catches any other accidental misshandling of Types. Triggered by things like, trying to
        # cast a string to a float etc...
        except TypeError:
            # Try one more way of getting usefuly data out of the metric, before giving up on it.
            try:
                val = float(metrics[metric])
                print ('indy_{metric}{{node_name="{node_name}",source="{label}"}} {value}'.format(
                        metric=metric.replace('-','_').replace(' ','_').lower(),
                        node_name=node_name,
                        label=label,
                        value=val
                    )
                )
            except ValueError:
                sys.stderr.write("Skipping unknown node metric (ValueError): '{}'\n".format(metric))
            except TypeError:
                sys.stderr.write("Skipping unknown node metric (TypeError): '{}'\n".format(metric))

    # Process view change information.
    vc_changed = node_info['View_change_status']['Last_view_change_started_at']
    vc_changed = time.mktime(
        time.strptime(
            vc_changed,
            '%Y-%m-%d %H:%M:%S'
        )
    )
    print('indy_last_view_change{{node_name="{node_name}",source="{label}"}} {vc_changed}'.format(
            node_name=node_name,
            label=label,
            vc_changed=vc_changed
        )
    )

    # Process consensus information.
    consensus_metrics = node_info['Freshness_status']
    in_consensus=0
    for metric in consensus_metrics:
        pool_num=consensus_metrics[metric]
        if not pool_num['Has_write_consensus']:
            in_consensus=in_consensus+1
    print('indy_consensus{{node_name="{node_name}",source="{label}"}} {consensus}'.format(
            node_name=node_name,
            label=label,
            consensus=in_consensus
        )
    )

process_map = {
    '1.5': _process_1_5,
    'latest': _process_1_5
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('GENESIS_URL', action="store")
    parser.add_argument('SEED', action="store")
    args = parser.parse_args()
    
    all_node_data = _get_metrics_live(args.GENESIS_URL,args.SEED)

    for node in all_node_data: 
        if 'response' not in node:
            # Do some sort of metric stating "node not responding"?
            continue
        data = node['response']['result']['data']
        if not data:
            sys.exit(1)
        try:
            node_ver = data['Software']['indy-node']
        except KeyError:
            try:
                node_ver = data['software']['indy-node']
            except KeyError:
                try:
                    cmd = ['/usr/bin/dpkg-query', '-f', "'${Version}\\n'", '-W', 'indy-node']
                    dpq = subprocess.Popen(cmd,shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                    dpq_out,dpq_stderr = dpq.communicate()
                    if dpq.returncode > 0:
                        sys.stderr.write(dpq_stderr)
                        sys.stderr.write("\nERROR: indy-node package isn't installed! Can't proceed\n")
                        sys.exit(2) 
                    node_ver = dpq_out.decode()
                except subprocess.SubprocessError:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    exc_str = "{}: {}".format(exc_type.__name__, exc_value)
                    sys.stderr.write("Subprocess Error during execution of command: {cmd} Error: '{exc_str}'".format(cmd=cmd, exc_str=exc_str))
                    sys.exit(2) 
        for v in [ node_ver, '.'.join(node_ver.split('.')[:-1]), 'latest' ]:
            try:
                process_metrics = process_map[v]
                break
            except KeyError:
                pass
        process_metrics()
