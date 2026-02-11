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
