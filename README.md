# Kafka-Pipeline-with-additional-services
this repo includes kafka, kafka-exporter, nginx, fluentbit and etc. a complete streamline of monitoring services.



Edit Volumes according to your linking.
contents of all config files are below : 


Fluent-bit.conf :

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
    Labels      job=$job, service=$service, event_type=$event_type, client_ip=$client_ip, user=$user, log_level=$log_level, user_id=$user_id, role=$role, device_type=$device_type, browser=$browser, os=$os, is_bot=$is_bot, failure_reason=$failure_reason, duration_ms=$duration_ms, http_status=$http_status, endpoint=$endpoint, status=$status, method=$method, user_agent=$user_agent, bytes_sent=$bytes_sent, error=$error, api_status=$api_status, retry_after=$retry_after, failed_attempts=$failed_attempts, rate_limited=$rate_limited
    Line_Format json

< ======================================================================================== >

parsers.conf :

[PARSER]
    Name        docker
    Format      json
    Time_Key    time
    Time_Format %Y-%m-%dT%H:%M:%S.%L
    Time_Keep   On
    
< ======================================================================================== >

parse_logs.lua : ( there also is a fastapi log parsers in this lua script, but i didnt remove them. i will post the fastapi login api just to test how much logs it creates. its interesting. dockerize the fastapi api and add to the pipeline.

function parse_log(tag, timestamp, record)
    local log = record["log"]
    
    if log == nil then
        record["job"] = "no-log"
        return 1, timestamp, record
    end
    
    local log_str = tostring(log)
    
    -- ==========================================
    -- ==========================================
    if string.find(log_str, '"service": "fastapi"', 1, true) or 
       string.find(log_str, '"service":"fastapi"', 1, true) then
        
        record["job"] = "fastapi"
        record["service"] = "fastapi"
        
        -- IP FastAPI
        local ip = string.match(log_str, '"ip": "([%d%.]+)"') or 
                   string.match(log_str, '"ip":"([%d%.]+)"')
        if ip then record["client_ip"] = ip end
        
        local event = string.match(log_str, '"event": "([^"]+)"') or
                      string.match(log_str, '"event":"([^"]+)"')
        if event then 
            record["event_type"] = event 
        end
        
        -- username
        local username = string.match(log_str, '"username": "([^"]+)"') or
                         string.match(log_str, '"username":"([^"]+)"')
        if username then record["user"] = username end
        
        -- ==========================================
        -- ==========================================
        
        -- Log Level
        local level = string.match(log_str, '"level": "([^"]+)"') or
                      string.match(log_str, '"level":"([^"]+)"')
        if level then record["log_level"] = level end
        
        -- User ID
        local user_id = string.match(log_str, '"user_id": (%d+)')
        if user_id then 
            record["user_id"] = user_id
        elseif string.find(log_str, '"user_id": null', 1, true) then
            record["user_id"] = "null"
        end
        
        -- Role
        local role = string.match(log_str, '"role": "([^"]+)"') or
                     string.match(log_str, '"role":"([^"]+)"')
        if role then record["role"] = role end
        
        -- Failure Reason
        local reason = string.match(log_str, '"reason": "([^"]+)"') or
                       string.match(log_str, '"reason":"([^"]+)"')
        if reason then record["failure_reason"] = reason end
        
        -- Device Type
        local device_type = string.match(log_str, '"device_type": "([^"]+)"') or
                            string.match(log_str, '"device_type":"([^"]+)"')
        if device_type then record["device_type"] = device_type end
        
        -- Browser
        local browser = string.match(log_str, '"browser": "([^"]+)"') or
                        string.match(log_str, '"browser":"([^"]+)"')
        if browser then record["browser"] = browser end
        
        -- OS
        local os = string.match(log_str, '"os": "([^"]+)"') or
                   string.match(log_str, '"os":"([^"]+)"')
        if os then record["os"] = os end
        
        -- Is Bot
        if string.find(log_str, '"is_bot": true', 1, true) then
            record["is_bot"] = "true"
        elseif string.find(log_str, '"is_bot": false', 1, true) then
            record["is_bot"] = "false"
        end
        
        -- Duration
        local duration = string.match(log_str, '"duration_ms": ([%d%.]+)')
        if duration then record["duration_ms"] = duration end
        
        -- Status (http_request)
        local status = string.match(log_str, '"status": (%d+)')
        if status then 
            record["api_status"] = status
            record["http_status"] = status
        end
        
        -- ==========================================
        -- ==========================================
        
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
    -- Nginx
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
    -- Kafka
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

< ======================================================================================== >

loki.yml : 

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

< ======================================================================================== >

prometheus.yml : 

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
        - "IP_OF_NODE_EXPORTER_DOCKER_CONTAIER:9100"
  - job_name: 'Loki'
    static_configs:
      - targets:
        - "loki:3100"
  - job_name: 'fluentbit'
    metrics_path: '/api/v1/metrics/prometheus'
    static_configs:
      - targets:
        - "fluentbit:2020"
       
  < ======================================================================================== >


Nginx.conf on your own. but remember to enable stub_status Module in the config file. 

  < ======================================================================================== >


rules.yml : ( dont pat attention to descriptions ! LOL )

groups:
  - name: kafka_down
    rules:
      - alert: KafkaDownFor10mins
        expr: kafka_brokers < 1 or absent(kafka_brokers) == 1
        for: 15s
        labels:
          severity: warning
        annotations:
          summary: "Kafka is not up"
          description: "Kafka has been down for 10 mins. take actions ASAP!!"
  - name: kafka_exporter_down
    rules:
      - alert: kafkaexporterDown
        expr: up{job="kafka-exporter"} == 0
        for: 30s
        labels:
          severity: warning
        annotations:
          summary: "kafka exporter down!"
          description: "kafka exporter has been down for 30s"
  - name: prometheus_job_missing
    rules:
      - alert: PrometheusJobMissing
        expr: up{job=~".*prometheus.*"} == 0
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Prometheus job missing (instance {{ $labels.instance }})"
          description: "A Prometheus job has disappeared\n  VALUE = {{ $value }}\n  LABELS = {{ $labels }}"
  - name: prometheus_not_connected_to_alertmanager
    rules:
      - alert: PrometheusNotConnectedToAlertmanager
        expr: prometheus_notifications_alertmanagers_discovered < 1
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Prometheus not connected to alertmanager (instance {{ $labels.instance }})"
          description: "Prometheus cannot connect the alertmanager\n  VALUE = {{ $value }}\n  LABELS = {{ $labels }}"
  - name: kafka_smells_data_loss
    rules:
      - alert: KafkaUnderReplicatedPartitions
        expr: sum(kafka_topic_partition_under_replicated_partition) > 0
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Data Loss(maybe)"
          description: "Detected partitions with fewer replicas than configured. \npotential data loss risk!!"
  - name: kafka_offline_partitions
    rules:
      - alert: KafkaOfflinePartitions
        expr: kafka_offline_partitions_count > 0
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Read and Write unavailable"
          description: "partitions are offline and unavailable for reads/writes."
  - name: Login_Brute_Force
    rules:
      - alert: LoginBruteForce
        expr: sum(rate(nginx_requests_total{job="nginx"}[5s])) by (ip) > 5
        for: 10s
        labels:
          severity: warning
        annotations:
          summary: "A BruteForce Attack is being Attemepted."
          description: "No Woories. the ip is now blocked"



  
