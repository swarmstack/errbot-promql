# errbot-promql

An Errbot plugin that queries Prometheus via it's API

For many of the built-in commands, you'll need to configure Prometheus to scrape your Alertmanagers and also your hosts via [NetData](https://my-netdata.io/)

## Installation:

```
!repos install https://github.com/swarmstack/errbot-promql.git

!plugin config PromQL {'PROMQL_URL': 'http://tasks.prometheus:9090/api/vi'}
```

## Usage:

```
PromQL

Query Prometheus via it's API

promql - Execute a PromQL query against Prometheus and return pretty json results
promql alerts - Current alert counts from Prometheus
promql cpu - Current averaged CPU metrics of all or partial host via NetData from Prometheus
promql cpufree - Current free CPU of all or partial host via NetData from Prometheus
promql lowest - Current lowest free CPU, memory, and root filesystem host via NetData from Pr...
promql lowestcpufree - Current lowest free CPU host via NetData from Prometheus
promql lowestmemfree - Current lowest free memory host NetData from Prometheus
promql lowestrootfree - Current lowest free root filesystem host via NetData from Prometheus
promql memfree - Current free memory of all or partial host via NetData from Prometheus
promql raw - Execute a PromQL query against Prometheus and return raw json results
promql rootfree - Current free root filesystem of all or partial host via NetData from Prometheus
```
