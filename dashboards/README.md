# Dashboards

This folder contains Grafana dashboards and a util directory with a python script that will take some of the output from run.sh (../fetch-validator-status/run.sh) and convert it to prometheus style output so that it can be read in and displayed in Grafana. The dashboards display Indy Network administrator type output that is useful for monitoring the status of an Indy Network as a whole and how well the indy-node software is running on each node. This readme contains a high level overview of the contents, then the detailed steps necessary to duplicate what can be seen on the public website [https://indymonitor.indiciotech.io](https://indymonitor.indiciotech.io). It also contains instructions for how to easily change a copy of one of the included dashboards to monitor a different network (plus all of the backend work needed).

The util/indy_metrics.py script originated from a contribution to Sovrin by Dan Farnsworth of Evernym under the Apache License.


## Overview

The indy-metrics.py script takes a genesis file and a seed as parameters, in that order.  The seed must evaluate to a valid DID for the network that has the TRUSTEE, STEWARD, or NETWORK_MONITOR role. 

The detailed instructions below explain how to set up, configure, start, and run the prometheus, grafana, node_exporter, Indy Node Monitor(run.sh), and indy_metrics.py to all work together to produce some “Admin style” metrics on a Grafana dashboard. Most of it is pretty normal if you are familiar with how the different items work, but there are a few tidbits that require advanced configuration (e.g. running multiple node_exporters with just 2 config files etc.).

Suggested future contributions to this leg of the project could include the following (feel free to add your own ideas here or work on one of the following suggestions if you like):



*   Dashboard colors to indicate Failure properly (current colors do not indicate anything except the defaults that occurred)
*   Drill-down to normal server hardware monitoring stats (Grafana dashboard 1860?) by clicking on the node names. Each node might need to run node_exporter locally.
*   Add Network Summary stats to the top of the dashboard   


## Setup on a Public AWS Server

These are the steps that I followed to set up the indymonitor.indiciotech.io Grafana website.  Please adjust them as needed for your own network(s) or configuration. These steps were originally written so that I could reproduce the public website setup that is now up and running. Many steps are optional or variable depending on your preferences. I am happy for any feedback containing suggestions for improvements.  



1. Install an AWS server:
    1. Step 1: Ubuntu 18.04
    2. Step 2: t3.small  (~$20USD/mo)
    3. Step 3: Protect against accidental termination
    4. Step 4: Change disk to 30G and uncheck “Delete on Termination”
    5. Step 6: Add Rule for HTTPS (Secure access to the Grafana webserver)
    6. Step 6: restrict port 22 to admin IP’s only 
    7. Defaults for the rest!
2. Launch instance and login
    1. Create new pem file indymon.pem
    2. Download it and move to (personal directory) ~/pems
    3. chmod 600 ~/pems/indymon.pem
    4. Add/use an elastic IP address if you don’t want the IP address to have a chance to change every time you boot the server (If you need help with this one, use step 21 of my “AWS Indy Node VM Install” document)
    5. ssh -i ~/pems/indymon.pem ubuntu@13.58.26.25
3. Install Docker
    1. curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    2. sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    3. sudo apt-get update
    4. sudo apt-get install docker-ce docker-ce-cli containerd.io
    5. sudo systemctl enable docker
    6. (no need to “start” docker. The docker daemon was started during the install step above...)
4. Clone and configure (change) run.sh script (from indy-node-monitor)
    1. mkdir ~/github
    2. cd ~/github
    3. git clone [https://github.com/bcgov/indy-node-monitor](https://github.com/bcgov/indy-node-monitor)
    4. vi indy-node-monitor/fetch-validator-status/run.sh
    5. Edit the file as follows
        1. Remove the -i for running docker (NO LONGER REQUIRED - after a recent PR)
        2. Add the full path to each “docker” command (for cron)
            1. /usr/bin/docker
5. Download and configure indy_metrics.py (these instructions will change when indy_metrics.py is checked in to github hyperledger/indy-node-monitor)
    1. Copy indy_metrics.py to the ~/github/indy-node-monitor/dashboards/util directory (where it will eventually reside without having to copy it in) 
        1. scp -i ~/pems/indymon.pem indy_metrics.py ubuntu@13.58.26.252:~/github/indy-node-monitor/dashboards/util
    2. vi ~/github/indy-node-monitor/dashboards/util/indy_metrics.py
        1. Change the location of run.sh in this file to match where it really is (fully qualified path is all I could get to work):
        5. /home/ubuntu/github/indy-node-monitor/fetch-validator-status/run.sh
6. Setup crontab to run indy_metrics.py for each network once every minute
    1. Create the output directories for node_exporter instances:
        1. sudo mkdir -p /var/log/node_exporter/9100
        2. sudo mkdir /var/log/node_exporter/9101
        3. sudo mkdir /var/log/node_exporter/9102
        4. sudo mkdir /var/log/node_exporter/9103
    2. sudo crontab -e 
```
    */1 * * * * python3 /home/ubuntu/github/indy-node-monitor/dashboards/util/indy_metrics.py https://raw.githubusercontent.com/Indicio-tech/indicio-network/master/genesis_files/pool_transactions_testnet_genesis (your ITN network monitor seed) >/var/log/node_exporter/9100/IndicioTestNet.prom
    */1 * * * * python3 /home/ubuntu/github/indy-node-monitor/dashboards/util/indy_metrics.py https://raw.githubusercontent.com/sovrin-foundation/sovrin/master/sovrin/pool_transactions_builder_genesis (your BuilderNet network monitor seed) >/var/log/node_exporter/9101/SovrinBuilderNet.prom
    */1 * * * * python3 /home/ubuntu/github/indy-node-monitor/dashboards/util/indy_metrics.py https://raw.githubusercontent.com/sovrin-foundation/sovrin/stable/sovrin/pool_transactions_sandbox_genesis (your StagingNet network monitor seed) >/var/log/node_exporter/9102/SovrinStagingNet.prom
    */1 * * * * python3 /home/ubuntu/github/indy-node-monitor/dashboards/util/indy_metrics.py https://raw.githubusercontent.com/sovrin-foundation/sovrin/stable/sovrin/pool_transactions_live_genesis (your SovrinMainNet  network monitor seed) >/var/log/node_exporter/9103/SovrinMainNet.prom
```
7. Download, install, and enable Prometheus 
    1. sudo groupadd --system prometheus  
    3. sudo useradd -s /sbin/nologin --system -g prometheus prometheus
    4. sudo mkdir /var/lib/prometheus 
    5. for i in rules rules.d files_sd; do sudo mkdir -p /etc/prometheus/${i}; done
    6. mkdir -p /tmp/prometheus && cd /tmp/prometheus
    7. curl -s https://api.github.com/repos/prometheus/prometheus/releases/latest | grep browser_download_url | grep linux-amd64 | cut -d '"' -f 4 | wget -qi -
    8. tar xvf prometheus*.tar.gz
    9. cd prometheus*/
    10. sudo mv prometheus promtool /usr/local/bin/
    11. prometheus --version
    12. sudo mv consoles/ console_libraries/ /etc/prometheus/
    13. sudo tee /etc/systemd/system/prometheus.service&lt;<EOF

            [Unit]
            Description=Prometheus
            Documentation=https://prometheus.io/docs/introduction/overview/
            Wants=network-online.target
            After=network-online.target

            [Service]
            Type=simple
            User=prometheus
            Group=prometheus
            ExecReload=/bin/kill -HUP \$MAINPID
            ExecStart=/usr/local/bin/prometheus   --config.file=/etc/prometheus/prometheus.yml   --storage.tsdb.path=/var/lib/prometheus   --web.console.templates=/etc/prometheus/consoles   --web.console.libraries=/etc/prometheus/console_libraries   --web.listen-address=0.0.0.0:9090   --web.external-url=
            SyslogIdentifier=prometheus
            Restart=always

            [Install]
            WantedBy=multi-user.target
            EOF

    13. cat /etc/systemd/system/prometheus.service
        1. To double check the file just created
    14. vi /etc/prometheus/prometheus.yml  

                global:
                  scrape_interval: 15s
                  evaluation_interval: 15s # Evaluate rules every 15 seconds.

                scrape_configs:
                  - job_name: 'node-external'
                    static_configs:
                      - targets: ['localhost:9100', 'localhost:9101','localhost:9102', 'localhost:9103']
                        labels:
                          group: 'prod-ext'

    15. for i in rules rules.d files_sd; do sudo chown -R prometheus:prometheus /etc/prometheus/${i}; done
    16. for i in rules rules.d files_sd; do sudo chmod -R 775 /etc/prometheus/${i}; done
    17. sudo chown -R prometheus:prometheus /var/lib/prometheus/
    18. sudo systemctl daemon-reload
    19. sudo systemctl start prometheus
    20. sudo systemctl enable prometheus
    21. systemctl status prometheus
8. Configure and enable Node_Exporter (multiple running instances)
    1. sudo useradd -rs /bin/false node_exporter
    2. mkdir -p /tmp/node_exporter && cd /tmp/node_exporter
    3. wget [https://github.com/prometheus/node_exporter/releases/download/v1.0.1/node_exporter-1.0.1.linux-amd64.tar.gz](https://github.com/prometheus/node_exporter/releases/download/v1.0.1/node_exporter-1.0.1.linux-amd64.tar.gz)
    4. tar xvzf node_exporter*.tar.gz
    5. cd node_exporter*/
    6. sudo mv node_exporter /usr/local/bin
    7. sudo chown node_exporter:node_exporter /usr/local/bin/node_exporter
    8. cd /etc/systemd/system
    9. Now create 2 system files that will start the multiple node_exporters needed to scrape the files from multiple Indy Networks. I used info from this site as a guide: [https://www.stevenrombauts.be/2019/01/run-multiple-instances-of-the-same-systemd-unit/](https://www.stevenrombauts.be/2019/01/run-multiple-instances-of-the-same-systemd-unit/)
    10. sudo vi node_exporters.target

            [Unit]
            Description=Node Exporters
            Requires=node_exporter@9100.service node_exporter@9101.service node_exporter@9102.service node_exporter@9103.service 

            [Install]
            WantedBy=multi-user.target

    11. sudo vi node_exporter@.service

            [Unit]
            Description=”Node Exporter on port %i”
            After=network-online.target
            PartOf=node_exporters.target

            [Service]
            User=node_exporter
            Group=node_exporter
            Type=simple
            ExecStart=/usr/local/bin/node_exporter --collector.textfile.directory /var/log/node_exporter/%i --web.listen-address=":%i"

            [Install]
            WantedBy=multi-user.target

    12. sudo systemctl daemon-reload
    13. sudo systemctl start node_exporters.target
9. Install, configure, enable, secure, Grafana as a web server (nginx)
    1. I relied heavily on the instructions found at [How To Install and Secure Grafana on Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-grafana-on-ubuntu-18-04)
    2. Setup domain names
        1. indymonitor.indiciotech.io
        2. [www.indymonitor.indiciotech.io](www.indymonitor.indiciotech.io) (I am not sure this one is required…)
    3. Install nginx by following the instructions at the 2 major links following:
        1. [How To Install Nginx on Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-18-04)
            1. Add these commands to what the guide has (near the beginning)
            2. sudo ufw allow 'OpenSSH'
            3. sudo ufw enable
            4. (also open ports 80 and 443 in your AWS or other firewalls)
            5. I also followed step 5 to set up a server block.
        2. [How To Secure Nginx with Lets Encrypt on Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-18-04)
            1. If everything runs correctly and you followed the steps in 9.2.1 then the following few commands should be all you need (this will save lots of reading and double-checking what you already did):
            2. sudo add-apt-repository ppa:certbot/certbot
            3. sudo apt install python-certbot-nginx
            4. sudo certbot --nginx -d indymonitor.indiciotech.io -d www.indymonitor.indiciotech.io
            5. To check if renewals will work:
                1. sudo certbot renew --dry-run
    4. Install grafana: (I used the following resource as an excellent guide, [How To Install and Secure Grafana on Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-grafana-on-ubuntu-18-04), but abbreviated many of the actions from step 1 and 2 here.)
        1. wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
        2. sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
        3. sudo apt update
        4. Verify that grafana is coming from the right place
            1. apt-cache policy grafana
            2. The following should be where it is getting grafana: [https://packages.grafana.com/oss/deb](https://packages.grafana.com/oss/deb)
        5. sudo apt install grafana
        6. sudo systemctl start grafana-server
        7. sudo systemctl status grafana-server
        8. sudo systemctl enable grafana-server
    5. Install a reverse proxy
        1. Follow step 2 (only) at [How To Install and Secure Grafana on Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-grafana-on-ubuntu-18-04) or the following abbreviated steps:
        2. sudo vi /etc/nginx/sites-available/indymonitor.indiciotech.io
            1. Delete the “try_files” line and replace it with 
            2. <code>proxy_pass [http://localhost:3000](http://localhost:3000);</code>
        3. sudo systemctl reload nginx
    6. Setup Grafana to allow for Anonymous(public) Access
        1. This is generally frowned upon, if I am not mistaken, because the data source will also be made public.  In this case, I believe the data is already public, so access to it is not bad.
        2. sudo vi /etc/grafana/grafana.ini
            1. Uncomment and change the following line in the [users] section
                1. allow_sign_up = false 
            2. Uncomment and change the following lines in the [auth.anonymous] section
                1. enabled = true
                2. org_name = Indy
                3. org_role = Viewer
        3. sudo systemctl restart grafana-server
    7. Login to your grafana server to complete the initial setup
        1. [https://indymonitor.indiciotech.io/login](https://indymonitor.indiciotech.io/login)
        2. admin admin (default login)
        3. Change the password as per the prompt to do so (this is required as your dashboards will be publicly available, but only alterable by the admin)
    8. Create an organization (matching what was added to the grafana.ini file)
        1. Click the shield on the bottom of the left menu bar and select ‘Orgs’
        2. Click “+ New org” then type in “Indy” and click ‘Create’
    9. Configure a data source
        1. Click the gear icon on the left menu and select ‘Data Sources’
        2. Click ‘Add data source’ and select ‘Prometheus’
    10. Create/Copy a dashboard
        1. Click the big + sign in the left menu, and select ‘Import’
        2. Upload the JSON file(s) matching the dashboard that you want to use as template (or initial) dashboards from the github repo ‘hyperledger/indy-node-monitor’.
        3. Repeat for as many dashboards as you would like to upload.
    11. Select a default Dashboard for your organization
        1. Select the dashboard that you want visitors to see when they come to the site.
        2. Next to the name of the dashboard in the upper left corner, click on the empty star to mark this dashboard as a favorite. (this can be done for multiple dashboards, but you will only end up selecting one as the final default dashboard)
        3. Click on the Gear icon in the left menu bar and select ‘Preferences’
        4. In ‘Home Dashboard’ select the dashboard that you want the public anonymous visitors to see when they first get to the site.


## Add a Dashboard for Another Network

The following instructions assume that you have configured a Grafana Dashboard similarly to the above steps and would like to make a similar dashboard for a different network.



1. On the monitoring server - add a new cron job line to get the validator info for the new network, (i.e. run the indy_metrics script with the appropriate genesis file and seed as parameters, and output the results to a new directory) For example to add a Sovrin DevNet:
    1. sudo mkdir /var/log/node_exporter/9104/
    2. */1 * * * * python3 /home/ubuntu/github/indy-node-monitor/dashboards/util/indy_metrics.py https://raw.githubusercontent.com/sovrin-foundation/sovrin/stable/sovrin/pool_transactions_dev_genesis (your Sovrin DevNet  network monitor seed) >/var/log/node_exporter/9104/SovrinDevNet.prom
2. Edit the node_exporters.target file to include the new networks port number. 
    1. sudo vi node_exporters.target
    2. Add “ node_exporter@9104.service” to the ‘Requires=’ line 

            [Unit]
            Description=Node Exporters
            Requires=node_exporter@9100.service node_exporter@9101.service node_exporter@9102.service node_exporter@9103.service node_exporter@9104.service

    3. sudo systemctl restart node_exporters.target
3. For Prometheus:
    1. sudo vi /usr/local/etc//prometheus.yml
    2. Add a target to the ‘node-external’ job targets line:
        1.       - targets: ['13.58.197.208:9100', 'localhost:9100', 'localhost:9101', 'localhost:9102', 'localhost:9103', 'localhost:9104']
    3. Restart Prometheus
        1. sudo systemctl restart prometheus
4. In grafana: 
    1. Make a copy of an existing Indy Dashboard
    2. Change the ‘node’ variable for the new dashboard to have the names of all of the network nodes in a comma separated list with quotes around each one.
        1. Select dashboard settings from the upper right menu.
        2. Select ‘variables’
        3. Change the node variable.
    3. Change all of the top panels' queries to point to (for example) “localhost:9104”
    4. Refresh the dashboard

This README.md and related code and dashboard submissions are freely donated to this project by Lynn Bendixsen, lynn@indicio.tech, and are subject to all open source licenses of the parent project hyperledger/indy-node-monitor.
