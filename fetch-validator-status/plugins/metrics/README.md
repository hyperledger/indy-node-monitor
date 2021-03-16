# Network Metrics

The [Network Metrics Plug-in](network_metrics.py) is used to create the resilience graph for the [metric dashboard](https://sovrin.org/ssi-metrics-dashboards/) on the [sovrin website](https://sovrin.org/) and could be used to log any other data to google sheets. This will append a row inside google sheets allowing you to log and create graphs off the monitor. Pair this with a cron job to run every 15 minutes or so and you have your own resilience log.

## Setup
In order to use the Network Metrics Plug-in your self you will need to create a folder named "conf" into the network metrics folder. That folder will need to have a google api credentials json file in it. Follow this [tutorial](https://www.youtube.com/watch?v=cnPlKLEGR7E&t=33s) on how to create the json file and how to set it up in google sheets. Make sure you watch the video to 3m 56s in order to set things up fully.

Your metrics plug-in should look somthing like this:

metrics\
----> conf\
--------> *GoogleAPI.json (Name it what ever you want)*\
----> google_sheets.py\
----> network_metrics.py\
----> README.md

## How To Use
Once that is set up, in order for you to run the plug-in the command will look something like this:\
`./run.sh --net ssn -v --mlog --json [Json File Name] --file [Google Sheet File Name] --worksheet [Worksheet name]`

--mlog: enables the plug-in\
--json: to specify which google API json file you would like to use inside the conf folder.\
--file: to specify which google sheet you would like to work in.\
--worksheet: to specify which worksheet you would like to work in, in the given google sheet file.

And your done!

