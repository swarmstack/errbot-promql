# errbot-promql

An Errbot plugin that queries Prometheus via it's API

For many of the built-in promql commands to work, you'll need to configure your Prometheus instance to scrape Alertmanagers as well as your hosts via [NetData](https://my-netdata.io/). This is done by default for [swarmstack](https://github.com/swarmstack/swarmstack) users who have installed Prometheus/Alertmanager/NetData using the swarmstack.yml playbook. If you wish to modify the included commands, consider forking this Github repo and altering promql.py for your own needs. The swarmstack [errbot-docker](https://github.com/swarmstack/errbot-docker) project also includes facilities for you to install locally-modified plugins directly into a Docker container if hosting your own copy via public or private repo isn't an option for you.

If you need an Errbot docker image, see [swarmstack/errbot-docker](https://github.com/swarmstack/errbot-docker), you will need to configure your Errbot's webserver (documented in that project) before proceeding to configure Errbot plugins such as errbot-promql below.

The default configuration string displayed by calling _!plugin config PromQL_ can be used as-shown below for [swarmstack](https://github.com/swarmstack/swarmstack) users. Otherwise, replace _http://prometheus_ (below) with your Prometheus _server IP or hostname_.

## Installation

```
repos install https://github.com/swarmstack/errbot-promql

plugin config PromQL {'PROMQL_URL': 'http://prometheus:9090/api/v1'}
```

## Updating

```
repos update swarmstack/errbot-promql
```

## Usage

```
You: help
c3po: 1:46PM
PromQL

Query Prometheus via it's API

promql <query> - Execute a PromQL query against Prometheus and return pretty json results
promql alerts - Current alert counts from Prometheus
promql cpu - Current averaged CPU metrics of all or partial host via NetData from Prometheus
promql cpufree - Current free CPU of all or partial host via NetData from Prometheus
promql lowest - Current lowest free CPU, memory, and root filesystem host via NetData from Pr...
promql lowestcpufree - Current lowest free CPU host via NetData from Prometheus
promql lowestmemfree - Current lowest free memory host NetData from Prometheus
promql lowestrootfree - Current lowest free root filesystem host via NetData from Prometheus
promql memfree - Current free memory of all or partial host via NetData from Prometheus
promql raw <query> - Execute a PromQL query against Prometheus and return raw json results
promql rootfree - Current free root filesystem of all or partial host via NetData from Prometheus
```

## Example

```
You: promql rootfree
c3po: 1:46 PM
Host: swarm01.example.com: 3.5GB (34%) root filesystem free
Host: swarm02.example.com: 2.2GB (22%) root filesystem free
Host: swarm03.example.com: 2.9GB (29%) root filesystem free

You: promql rootfree 01
c3po: 1:46 PM
Host: swarm01.example.com: 3.5GB (34%) root filesystem free

You: promql lowest
c3po: 1:46 PM
Host: swarm02.example.com: 97.7% cpu idle
Host: swarm03.example.com: 28269MB (93%) memory free/cached
Host: swarm42.example.com: 2.2GB (22%) root filesystem free

You: promql bottomk(1, alertmanager_alerts{state="active"})
c3po: 1:46 PM
{
"status": "success",
"data": {
    "resultType": "vector",
    "result": [
        {
            "metric": {
                "__name__": "alertmanager_alerts",
                "instance": "10.0.6.153:9093",
                "job": "alertmanager",
                "state": "active"
            },
            "value": [
                1540670301.383,
                "0"
            ]
        }
    ]
}
}
