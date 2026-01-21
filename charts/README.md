# Helm chart for the Indy-Monitoring-Stack

_**Work in progress, for development use only.**_

## Pre-requisites

*   K8s or minikube cluster
*   Helm v3+ binaries
*   Registered Indy network monitor seed

## Quickstart

### Configuring the deployment

1.  Clone and edit the [**extra_vars.template**](./extra_vars.template) to a file called **extra_vars.yaml**.
    
        cp extra_vars.template extra_vars.yaml

2.  Edit the inputs. For some reference you can look at the [**config/indy_node_monitor/networks.json**](./config/indy_node_monitor/networks.json) file. You can add as many as you want. You must include a registered network monitor seed for your selected networks.

    Here is an example for the soverin network:
    ```plaintext
    inputs:
      - name: Sovrin Builder Net
        short_name: sbn
        genesis_url: https://raw.githubusercontent.com/sovrin-foundation/sovrin/stable/sovrin/pool_transactions_builder_genesis
        network_monitor_seed: INSERT_REGISTERED_NETWORK_MONITOR_SEED_HERE
      - name: Sovrin Staging Net
        short_name: ssn
        genesis_url: https://raw.githubusercontent.com/sovrin-foundation/sovrin/stable/sovrin/pool_transactions_sandbox_genesis
        network_monitor_seed: INSERT_REGISTERED_NETWORK_MONITOR_SEED_HERE
      - name: Sovrin Main Net
        short_name: smn
        genesis_url: https://raw.githubusercontent.com/sovrin-foundation/sovrin/stable/sovrin/pool_transactions_live_genesis
        network_monitor_seed: INSERT_REGISTERED_NETWORK_MONITOR_SEED_HERE
    ```
3.  Set the secrets to something secure. Make sure you keep a copy of your credential in safe keystore such as a password manager or vault.
4.  (optional) If you want to expose services, set the **ingress** to `True`, enter your **domain** and **endpoints**.

### Deployment

Once you are happy with the configuration, create the namespace and deploy the stack. Here's a one liner that will take care of this for you. Make sure the namespace name matches the **extra_vars.yaml** file.

```plaintext
helm upgrade indy-monitoring-stack . \
    --namespace indy-monitoring-stack \
    --values ./extra_vars.yaml \
    --create-namespace --install

```

## Advanced configuration

You can edit the ports for the applications but this is not recommended. Some ports are statically set in the configuration files and it might break things if you are not sure about what you are doing. It is recommeneded to keep the ports as they are defined in the [**values.yaml**](./values.yaml) file.

### Service configuration

All service configurations are located in the [**config/**](./config/) folder under their respective application directory. These configurations are loaded as configmaps during deployment and injected into the pods. 

You can apply a new configuration by editing these files and redeploying the stack.

### Dashboard development

You can export a dashboard from grafana after you customized it and add the ***.json** file generated under [**config/grafana/dashboards/**](./config/grafana/dashboards/)

All dashboards from that directory are automatically loaded when redeploying the stack.
