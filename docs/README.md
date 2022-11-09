<!-- Commands -->


# Command List


## Usage:
````bash
        ./manage [options] [command] [args]
````
---


### List
````bash
        list
````
* Get a list of commands


### Start
````bash
        up [service]
or      
        start [service]
````
* Spin up the Indy Node Monitoring Stack environment.
    > Optionally specify the service to spin up (dependencies will also be spun up).


### Stop
````bash
        down [service]
or
        stop [service]    
````
* Tear down the Indy Node Monitoring Stack environment.
    > Optionally specify the service to tear down.


### Restart
````bash
        restart [service]    
````
* Restart the Indy Node Monitoring Stack environment.
    > Optionally specify the service to restart.


### Services
````bash
        list-services    
````
* Get a list of the services that make up the Indy Node Monitoring Stack.


### Logs
````bash
        logs <service>
````
* Stream the logs from a given container.


### Shell
````bash
        shell <service>
````
* Open a shell on a given container.


### Plugins
````bash
        install-plugin
````
* Install a Grafana plug-in on the Grafana container.


### Clearing Data
````bash
        delete-data [service]
````
* Delete the data for a given service, or all services by default. 
    > This is useful to clear data from Prometheus and/or InfluxDB when making changes to how the data is collected.


### Cleaning Environment
````bash
    clean
````
* Cleans up all environment resources.
    > Deletes data from all services

    > Deletes all containers images and prunes any dangling images.


### Influx CLI Shell
````bash
    influx-cli
````
* Open a shell to the Influx CLI on the influxDB container.


### Flux REPL Shell
````bash
    flux-repl
````
* Open a shell to the Flux REPL on the influxDB container.


### Builds
````bash
    build [service]
````
* Use for troubleshooting builds when making image configuration changes.
    > Builds container images based on the docker-compose configuration.


### Parsing Test
````bash
    Sed-test
````
* Run a 'sed' parsing test on your machine.
    > Helps diagnose issues with the version of 'sed' on some machines.

---


## Options:


````bash
    -h
````
* Print this help documentation.


````bash
        --nightly
````
* Build/Use 'nightly' Influx images, 'latest' images are built/used by default.
    > Works with the up|start and restart commands.


<br>

<!-- Installing Indy Node Monitoring Stack -->

<!-- NOT FINISHED YET -->

<!-- Setting up the Monitoring Stack -->

# Setting up the Monitoring Stack
Once you have the Indy Node Monitoring Stack on your system, right click the folder and open it in VS Code.

* Find .env-seeds
* Insert your seeds for each SBN, SSN, and SMN
* Make sure to save the file before closing

<br>

<!-- Adding Dashboards to the stack -->


# Adding new dashboards to the stack
* Create a new dashboard in the Grafana UI
* Save JSON file to your computer
* Open your *"c:/indy-node-monitor"* folder
* Navagate to:
    * *"grafana"*
    * *"provisioning"*
    * *"dashboards"*
* Place JSON file in this folder


<br>


<!-- Saving changes to existing dashboards-->

# Saving changes to existing dashboards
**NOTE: The *"Copy JSON to clipboard"* button tends to NOT work!**

* Click into the raw JSON, use *Ctrl+A* & *Ctrl+C*
* Navagate to *"c:/indy-node-monitor"*
* Right click the *"c:/indy-node-monitor"* folder and open in Visual Studio Code
* In VS-Code, navigate to:
    * *"grafana"*
    * *"provisioning"*
    * *"dashboards"*
    * Find the dashboard you are working on

**NOTE: Make sure you are changing the CORRECT dashboard!**

* Select everything in the VS-Code file for the dashboard you are working on and paste the new changes
* Make sure to save the file before closing VS-Code


<br>


<!-- Prometheus Query Example -->

# Prometheus Query Example
#### Example
````promQL
    node_response_result_data_Pool_info_reachable_node_count
````
This is looking at the *"reachable node count"* under *"pool info"*, under *"data"*, under *"result"* etc..

> If you don't know your metric names, the metrics browser button helps you see the names of all metrics Prometheus can see. This is assuming the data source is working correctly.


<br>


<!-- Influx Query Example -->

# InfluxDB (flux) Query Example
````flux
    from(bucket: v.defaultBucket)
        |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
        |> filter(fn: (r) =>
            r._measurement == "node" and
            r._field == "node-address"
    )
````

**from()** defines your bucket
\
\
**range()** limits the query data by time
\
\
**filter()** limits what rows of data will be output
> Filters have a *fn* parameter to dictate if values are true or false *(fn: (r))*. If the parameter evaluates the row to be true it will be included in the output data.

<br>

**r._measurement** is what we are measuring by
\
\
**r._field** is the field of data we want to output


<br>


<!-- Data Sources
# Telegraf

# Restful API

TBD
-->


<!-- Alerting -->

<!-- NOT FINISHED -->
# Alerts
Alerts trigger an action (*commonly an email or slack message*) when certain requirements are met.
\
\
Most commonly a separate dashboard is created as the "Alerts Dashboard". A saparate dashboard is typically used because what is displayed to set triggers is often bare compared to the main visual dashboards.
\
\
The Alert Dashboard only requires the metric you want to trigger the alert and the threshold at which the metric triggers the alert.


<br>


<!-- Variable Filters -->

# Drop-Down/Variable Filters
To set variables you need to go to the settings icon located at the top right in the Grafana the dashboard you are working on. Then select the variables tab on the left side.
\
\
Variables call upon *key_tags* as values.

* The _**name**_ of the variable you set will be used to filter your metrics

<br>

* The _**label**_ is used as the name displayed in the drop-down list



#### Example 1
````
        label_values()
````
>This is your base query for making filters. A *key_tag* goes in the brackets to call the values as your list of choices.


#### Example 2
````
        label_values(name)
````
This creates a label value for *"name"* which will make a list of every node name from our data source since our *key_tag* for node names is *"name"* 

>If your query is working there should be a list of expected values in the preview of values section at the bottom.


<br>


<!-- Cascading Filters-->

# Cascading Filters
#### Example
````
        label_values(node_response_result_data_Pool_info_Reachable_nodes_count{name="[[node]]"}, network)
````

**label_values()**  is our base query to create the variable
\
\
**node_response_result_data_pool_info_reachable_nodes_count** is our example metric wich is calling ALL reachable nodes
\
\
**{name="[[node]]"}** *"name"* is the metric output for the name of each node. Calling the variable we created in the section above using *"[[node]]"*, we can compare the metric output with our variable.

>This format is used in the mertic queries as well so you can pick and choose which metrics you want to change based upon the filters.

<br>

**", networks)"**  is, in this case, a *key_tag* following the filtered metric query which we want to use as our variable for this cascading filter. Our *key_tag*, "networks", lists all of the networks from our data source.
\
\
The end result, when we select a node from our first filter, the second filter will ONLY show networks that the node is on. So if a node is on multiple networks, we can show the data per netowrk rather than the sum of multiple networks.


<br>


<!-- Filters in Prom queries-->

# Filters in Prometheus queries
#### Example
````
        example_metric{job="tick"}
````
We filter our data by job, which in our case is *"tick"*

**NOTE: A "Job" can be set in the data source**


<br>



<!-- Grafana variables in Prom queries-->

# Implimenting Grafana variables in Prometheus queries
#### Example
````
        example_metric{name="[[node]]"}
````
This example compares the *variable* *"[[Node]]"* **(Being the name of the variable, NOT the label title)** to the *key_tag* *"name"*. 
\
\
As a result, when filtered using the Grafana drop-down, only metric values associated with the node selected will be shown.


<br>


<!-- Grafana variables in InfluxDB queries-->

# Implimenting Grafana variables in InfluxDB (flux) queries
#### Example
````
        from(bucket: v.defaultBucket)
            |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
            |> filter(fn: (r) =>
            r._measurement == "node" and
            r._field == "node-address" and
            r.name == "${node}" and
            r.network == "${network}"
        )
````

**from()** defines your bucket
\
\
**range()** limits the query data by time
\
\
**filter()** limits what rows of data will be output
> Filters have a *fn* parameter to dictate if values are true or false *(fn: (r)). If the parameter evaluates the row to be true it will be included in the output data.

<br>

**r._measurement** is what we are measuring by
\
\
**r._field** is the field of data we want to output
\
\
**r.name** & **r.network** is referencing *key_tags*
\
\
**\${node}** and **\${network}** is referencing Grafana variables


<br>


<!-- Troubleshooting -->
# Troublshooting


### Dashboard showing no data
> The monitoring stack doesn't always start up properly, as a result the dashboards might not be populated. Running the restart command in the monitoring stack should fix the issue.

