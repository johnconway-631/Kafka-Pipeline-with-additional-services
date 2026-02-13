# 🚀 Kafka Observability Pipeline

<div align="center">

![Architecture](https://img.shields.io/badge/Architecture-Microservices-blue?style=for-the-badge)
![Stack](https://img.shields.io/badge/Stack-Kafka|Loki|Prometheus|Grafana-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production_Ready-success?style=for-the-badge)

**Enterprise-grade log aggregation & monitoring infrastructure with intelligent parsing**

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Log Parsing Engine](#log-parsing-engine)
- [Alerting Rules](#alerting-rules)
- [Services](#services)
- [Volumes](#volumes)

---

## 🎯 Overview

This repository provides a **production-ready observability stack** built around Apache Kafka, featuring:

- 🔥 **Real-time log streaming** via Fluent Bit with custom Lua parsers
- 📊 **Centralized log storage** with Grafana Loki
- 📈 **Multi-dimensional metrics** collection via Prometheus
- 🚨 **Intelligent alerting** for infrastructure and security events
- 🔄 **Service mesh monitoring** covering Nginx, FastAPI, and Kafka internals

> 💡 **Designed for scale**: Handles high-throughput log ingestion with structured parsing and automatic enrichment.

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   FastAPI App   │     │   Nginx Proxy   │     │   Kafka Cluster   │
│  (JSON Logs)    │     │ (Access Logs)   │     │  (Broker Logs)    │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │    Fluent Bit       │
                    │  (Log Collector)    │
                    │  • Tail Input       │
                    │  • Lua Parsing      │
                    │  • Loki Output      │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
     ┌────────▼────────┐ ┌─────▼──────┐ ┌──────▼──────┐
     │   Grafana Loki  │ │ Prometheus │ │   Grafana   │
     │  (Log Storage)  │ │  (Metrics) │ │(Dashboards) │
     └─────────────────┘ └────────────┘ └─────────────┘
```

---

## ⚡ Quick Start

```bash
# Clone and navigate
git clone <repo-url>
cd kafka-observability-pipeline

# Configure volumes (see Volumes section)
# Edit docker-compose.yml volume paths

# Launch stack
docker-compose up -d

# Verify services
docker-compose ps

# Access dashboards
# Grafana: http://localhost:3000
# Prometheus: http://localhost:9090
```

---

## ⚙️ Configuration

### Fluent Bit (`fluent-bit.conf`)

High-performance log collector with Docker-aware tailing:

```ini
[SERVICE]
    Flush        1
    Daemon       Off
    Log_Level    info
    Parsers_File parsers.conf
    HTTP_Server  On
    HTTP_Listen  0.0.0.0
    HTTP_Port    2020

[INPUT]
    Name          tail
    Path          /var/lib/docker/containers/*/*.log
    Parser        docker
    Tag           docker.*
    Docker_Mode   On
    Buffer_Chunk_Size 1MB
    Buffer_Max_Size   5MB

[FILTER]
    Name   lua
    Match  docker.*
    Script /fluent-bit/etc/parse_logs.lua
    Call   parse_log

[OUTPUT]
    Name        loki
    Match       docker.*
    Host        loki
    Port        3100
    Labels      job=$job, service=$service, event_type=$event_type, 
                client_ip=$client_ip, user=$user, log_level=$log_level, 
                user_id=$user_id, role=$role, device_type=$device_type, 
                browser=$browser, os=$os, is_bot=$is_bot, 
                failure_reason=$failure_reason, duration_ms=$duration_ms, 
                http_status=$http_status, endpoint=$endpoint, status=$status, 
                method=$method, user_agent=$user_agent, bytes_sent=$bytes_sent, 
                error=$error, api_status=$api_status, retry_after=$retry_after, 
                failed_attempts=$failed_attempts, rate_limited=$rate_limited
    Line_Format json
```

### Parsers (`parsers.conf`)

```ini
[PARSER]
    Name        docker
    Format      json
    Time_Key    time
    Time_Format %Y-%m-%dT%H:%M:%S.%L
    Time_Keep   On
```

### Loki (`loki.yml`)

```yaml
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory

schema_config:
  configs:
  - from: 2020-05-15
    store: tsdb
    object_store: filesystem
    schema: v13
    index:
      prefix: index_
      period: 24h

ruler:
  alertmanager_url: http://alertmanager:9093
```

### Prometheus (`prometheus.yml`)

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - "alertmanager:9093"

rule_files:
  - "rules.yml"

scrape_configs:
  - job_name: "kafka-exporter"
    static_configs:
      - targets:
        - "kafka-exporter:9308"
    scrape_interval: 10s

  - job_name: "prometheus"
    static_configs:
      - targets:
        - "localhost:9090"

  - job_name: "alertmanager"
    static_configs:
      - targets:
        - "alertmanager:9093"

  - job_name: 'nginx-exporter'
    static_configs:
      - targets: 
        - "nginx-exporter:9113"
    scrape_interval: 10s
    
  - job_name: 'node'
    static_configs:
      - targets:
        - "IP_OF_NODE_EXPORTER_DOCKER_CONTAINER:9100"
        
  - job_name: 'Loki'
    static_configs:
      - targets:
        - "loki:3100"
        
  - job_name: 'fluentbit'
    metrics_path: '/api/v1/metrics/prometheus'
    static_configs:
      - targets:
        - "fluentbit:2020"
```

---

## 🧠 Log Parsing Engine

The heart of this pipeline is a **custom Lua parser** that intelligently routes and enriches logs from multiple services:

### Features

| Service | Parsing Logic | Enriched Fields |
|---------|--------------|-----------------|
| **FastAPI** | JSON log parsing | `user_id`, `role`, `device_type`, `browser`, `os`, `is_bot`, `duration_ms`, `failure_reason`, `rate_limited`, `failed_attempts` |
| **Nginx** | Regex pattern matching | `client_ip`, `endpoint`, `method`, `status`, `bytes_sent`, `user_agent`, `error` |
| **Kafka** | Keyword detection | Service identification, broker health |

### Lua Parser (`parse_logs.lua`)

```lua
function parse_log(tag, timestamp, record)
    local log = record["log"]
    
    if log == nil then
        record["job"] = "no-log"
        return 1, timestamp, record
    end
    
    local log_str = tostring(log)
    
    -- ==========================================
    -- FastAPI Application Logs
    -- ==========================================
    if string.find(log_str, '"service": "fastapi"', 1, true) or 
       string.find(log_str, '"service":"fastapi"', 1, true) then
        
        record["job"] = "fastapi"
        record["service"] = "fastapi"
        
        -- IP Extraction
        local ip = string.match(log_str, '"ip": "([%d%.]+)"') or 
                   string.match(log_str, '"ip":"([%d%.]+)"')
        if ip then record["client_ip"] = ip end
        
        -- Event Classification
        local event = string.match(log_str, '"event": "([^"]+)"') or
                      string.match(log_str, '"event":"([^"]+)"')
        if event then 
            record["event_type"] = event 
        end
        
        -- User Context
        local username = string.match(log_str, '"username": "([^"]+)"') or
                         string.match(log_str, '"username":"([^"]+)"')
        if username then record["user"] = username end
        
        -- Security Context
        local level = string.match(log_str, '"level": "([^"]+)"') or
                      string.match(log_str, '"level":"([^"]+)"')
        if level then record["log_level"] = level end
        
        local user_id = string.match(log_str, '"user_id": (%d+)')
        if user_id then 
            record["user_id"] = user_id
        elseif string.find(log_str, '"user_id": null', 1, true) then
            record["user_id"] = "null"
        end
        
        local role = string.match(log_str, '"role": "([^"]+)"') or
                     string.match(log_str, '"role":"([^"]+)"')
        if role then record["role"] = role end
        
        local reason = string.match(log_str, '"reason": "([^"]+)"') or
                       string.match(log_str, '"reason":"([^"]+)"')
        if reason then record["failure_reason"] = reason end
        
        -- Device Intelligence
        local device_type = string.match(log_str, '"device_type": "([^"]+)"') or
                            string.match(log_str, '"device_type":"([^"]+)"')
        if device_type then record["device_type"] = device_type end
        
        local browser = string.match(log_str, '"browser": "([^"]+)"') or
                        string.match(log_str, '"browser":"([^"]+)"')
        if browser then record["browser"] = browser end
        
        local os = string.match(log_str, '"os": "([^"]+)"') or
                   string.match(log_str, '"os":"([^"]+)"')
        if os then record["os"] = os end
        
        if string.find(log_str, '"is_bot": true', 1, true) then
            record["is_bot"] = "true"
        elseif string.find(log_str, '"is_bot": false', 1, true) then
            record["is_bot"] = "false"
        end
        
        -- Performance Metrics
        local duration = string.match(log_str, '"duration_ms": ([%d%.]+)')
        if duration then record["duration_ms"] = duration end
        
        local status = string.match(log_str, '"status": (%d+)')
        if status then 
            record["api_status"] = status
            record["http_status"] = status
        end
        
        -- Rate Limiting Context
        local failed_attempts = string.match(log_str, '"failed_attempts_window": (%d+)')
        if failed_attempts then 
            record["failed_attempts"] = failed_attempts 
        else
            if string.find(log_str, '"failed_attempts_window": null', 1, true) then
                record["failed_attempts"] = "0"
            end
        end
        
        local retry_after = string.match(log_str, '"retry_after": (%d+)')
        if retry_after then 
            record["retry_after"] = retry_after 
        else
            record["retry_after"] = "0"
        end
        
        if event == "login_blocked" then
            record["rate_limited"] = "true"
        elseif event == "login_failed" or event == "login_success" then
            record["rate_limited"] = "false"
        else
            record["rate_limited"] = "unknown"
        end
        
    -- ==========================================
    -- Nginx Access Logs
    -- ==========================================
    elseif string.match(log_str, "%d+%.%d+%.%d+%.%d+") and 
           (string.find(log_str, "HTTP/", 1, true)) then
        
        record["job"] = "nginx"
        record["service"] = "nginx"
        
        local ip = string.match(log_str, "(%d+%.%d+%.%d+%.%d+)")
        if ip then record["client_ip"] = ip end

        local method, endpoint = string.match(log_str, '"(%u+)%s+([^%s]+)%s+HTTP')
        if endpoint then record["endpoint"] = endpoint end
        
        local status = string.match(log_str, '"%s+(%d%d%d)%s')
        if status then 
            record["status"] = status 
            record["http_status"] = status
        end

        local user_agent = string.match(log_str, '"[^"]*"%s+"([^"]+)"')
        if user_agent then record["user_agent"] = user_agent end

        if method then record["method"] = method end

        local bytes_sent = string.match(log_str, '"%s+%d%d%d%s+(%d+)')
        if bytes_sent then 
            record["bytes_sent"] = bytes_sent 
        end

        if status then 
            local code = tonumber(status)
            if code >= 400 then 
                record["error"] = status
            end
        end
        
        record["rate_limited"] = "n/a"
        record["retry_after"] = "0"
        record["failed_attempts"] = "0"
        record["event_type"] = "http_request"
        
    -- ==========================================
    -- Kafka Infrastructure
    -- ==========================================
    elseif string.find(log_str, "kafka", 1, true) or 
           string.find(log_str, "zookeeper", 1, true) then
        record["job"] = "kafka"
        record["service"] = "kafka"
        record["rate_limited"] = "n/a"
        record["retry_after"] = "0"
        record["failed_attempts"] = "0"
    else
        record["job"] = "other"
        record["service"] = "other"
        record["rate_limited"] = "n/a"
        record["retry_after"] = "0"
        record["failed_attempts"] = "0"
    end
    
    return 1, timestamp, record
end
```

---

## 🚨 Alerting Rules

### Infrastructure Monitoring (`rules.yml`)

```yaml
groups:
  - name: kafka_health
    rules:
      - alert: KafkaDownFor10mins
        expr: kafka_brokers < 1 or absent(kafka_brokers) == 1
        for: 15s
        labels:
          severity: warning
        annotations:
          summary: "Kafka cluster unavailable"
          description: "Kafka has been down for 10 minutes. Immediate action required!"
          
      - alert: KafkaUnderReplicatedPartitions
        expr: sum(kafka_topic_partition_under_replicated_partition) > 0
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Potential data loss detected"
          description: "Partitions have fewer replicas than configured. Risk of data loss!"
          
      - alert: KafkaOfflinePartitions
        expr: kafka_offline_partitions_count > 0
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Read/Write operations unavailable"
          description: "Partitions are offline and unavailable for reads/writes."

  - name: exporter_health
    rules:
      - alert: KafkaExporterDown
        expr: up{job="kafka-exporter"} == 0
        for: 30s
        labels:
          severity: warning
        annotations:
          summary: "Kafka exporter down"
          description: "Kafka exporter has been down for 30s"
          
      - alert: PrometheusJobMissing
        expr: up{job=~".*prometheus.*"} == 0
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Prometheus job missing (instance {{ $labels.instance }})"
          description: "A Prometheus job has disappeared\n  VALUE = {{ $value }}\n  LABELS = {{ $labels }}"
          
      - alert: PrometheusNotConnectedToAlertmanager
        expr: prometheus_notifications_alertmanagers_discovered < 1
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Prometheus not connected to alertmanager"
          description: "Prometheus cannot connect to alertmanager\n  VALUE = {{ $value }}\n  LABELS = {{ $labels }}"

  - name: security_monitoring
    rules:
      - alert: LoginBruteForce
        expr: sum(rate(nginx_requests_total{job="nginx"}[5s])) by (ip) > 5
        for: 10s
        labels:
          severity: warning
        annotations:
          summary: "Brute force attack detected"
          description: "High frequency login attempts detected. IP blocking recommended."
```

---

## 🔧 Services

| Service | Port | Purpose | Health Check |
|---------|------|---------|--------------|
| **Kafka** | 9092 | Message broker | `kafka-brokers` metric |
| **Kafka Exporter** | 9308 | Kafka metrics | HTTP `/metrics` |
| **Zookeeper** | 2181 | Coordination | TCP connection |
| **Fluent Bit** | 2020 | Log collection | HTTP `/api/v1/metrics` |
| **Loki** | 3100 | Log storage | HTTP `/ready` |
| **Prometheus** | 9090 | Metrics storage | HTTP `/-/healthy` |
| **Grafana** | 3000 | Visualization | HTTP `/api/health` |
| **Alertmanager** | 9093 | Alert routing | HTTP `/-/healthy` |
| **Nginx** | 80/443 | Reverse proxy | `stub_status` module |
| **Nginx Exporter** | 9113 | Nginx metrics | HTTP `/metrics` |
| **Node Exporter** | 9100 | System metrics | HTTP `/metrics` |

---

## 💾 Volumes

> ⚠️ **Important**: Update volume paths in `docker-compose.yml` to match your environment.

```yaml
volumes:
  # Persistent storage
  kafka-data:
    driver: local
  zookeeper-data:
    driver: local
  loki-storage:
    driver: local
  prometheus-data:
    driver: local
  grafana-storage:
    driver: local
  
  # Configuration mounts (update these paths)
  fluent-bit-config:
    type: bind
    source: /path/to/your/fluent-bit.conf
    target: /fluent-bit/etc/fluent-bit.conf
    
  parsers-config:
    type: bind
    source: /path/to/your/parsers.conf
    target: /fluent-bit/etc/parsers.conf
    
  lua-scripts:
    type: bind
    source: /path/to/your/parse_logs.lua
    target: /fluent-bit/etc/parse_logs.lua
    
  loki-config:
    type: bind
    source: /path/to/your/loki.yml
    target: /etc/loki/local-config.yaml
    
  prometheus-config:
    type: bind
    source: /path/to/your/prometheus.yml
    target: /etc/prometheus/prometheus.yml
    
  alert-rules:
    type: bind
    source: /path/to/your/rules.yml
    target: /etc/prometheus/rules.yml
    
  nginx-config:
    type: bind
    source: /path/to/your/nginx.conf
    target: /etc/nginx/nginx.conf
```

### Nginx Configuration Note

Ensure `stub_status` module is enabled in `nginx.conf`:

```nginx
server {
    listen 80;
    
    location /nginx_status {
        stub_status on;
        allow 127.0.0.1;
        allow 172.0.0.0/8;  # Docker network
        deny all;
    }
}
```

---

## 🧪 Testing

The repository includes a **FastAPI authentication service** for load testing:

```bash
# Build and run the test API
docker build -t fastapi-auth-test ./fastapi-api/
docker run -d -p 8000:8000 fastapi-auth-test

# Generate load (install hey or use curl)
hey -z 30s -c 10 http://localhost:8000/login
```

This generates realistic authentication logs for testing the parsing pipeline.

---

<div align="center">

**Built with ❤️         **

*Production-tested • Scalable • Observable*

</div>
