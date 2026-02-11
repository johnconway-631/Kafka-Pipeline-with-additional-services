from fastapi import FastAPI, APIRouter, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from user_agents import parse
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading

class SimpleRateLimiter:
   
    def __init__(self, max_attempts: int = 5, window_seconds: int = 60, block_duration: int = 300):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.block_duration = block_duration
        
        self._storage: Dict[str, dict] = {}
        self._lock = threading.Lock()
    
    def _cleanup_old_attempts(self, ip: str, current_time: float):
        if ip not in self._storage:
            return
        
        cutoff_time = current_time - self.window_seconds
        attempts = self._storage[ip].get("attempts", [])
        self._storage[ip]["attempts"] = [
            attempt for attempt in attempts 
            if attempt["time"] > cutoff_time and not attempt["success"]
        ]
    
    def is_blocked(self, ip: str) -> tuple[bool, Optional[int]]:
        current_time = time.time()
        
        with self._lock:
            if ip not in self._storage:
                return False, None
            
            blocked_until = self._storage[ip].get("blocked_until")
            if blocked_until and current_time < blocked_until:
                remaining = int(blocked_until - current_time)
                return True, remaining
            
            if blocked_until and current_time >= blocked_until:
                self._storage[ip]["blocked_until"] = None
            
            return False, None
    
    def record_attempt(self, ip: str, success: bool) -> tuple[bool, Optional[int], int]:
        current_time = time.time()
        
        with self._lock:
            if ip not in self._storage:
                self._storage[ip] = {"attempts": [], "blocked_until": None}
            
            if success:
                self._storage[ip]["attempts"] = []
                self._storage[ip]["blocked_until"] = None
                return False, None, 0
            
            self._cleanup_old_attempts(ip, current_time)
            
            self._storage[ip]["attempts"].append({
                "time": current_time,
                "success": False
            })
            
            failed_count = len(self._storage[ip]["attempts"])
            
            if failed_count >= self.max_attempts:
                block_until = current_time + self.block_duration
                self._storage[ip]["blocked_until"] = block_until
                return True, self.block_duration, failed_count
            
            return False, None, failed_count
    
    def get_status(self, ip: str) -> dict:
        current_time = time.time()
        
        with self._lock:
            if ip not in self._storage:
                return {"attempts": 0, "blocked": False}
            
            self._cleanup_old_attempts(ip, current_time)
            blocked_until = self._storage[ip].get("blocked_until")
            
            return {
                "attempts": len(self._storage[ip]["attempts"]),
                "blocked": blocked_until is not None and current_time < blocked_until,
                "blocked_until": datetime.fromtimestamp(blocked_until).isoformat() if blocked_until else None
            }

login_rate_limiter = SimpleRateLimiter(
    max_attempts=5,
    window_seconds=60,
    block_duration=300
)

USERS_db = {
    "admin": {"id": 1001, "password": "secret", "role": "admin"},
    "alex": {"id": 1002, "password": "alex", "role": "user"},
    "mikee": {"id": 1003, "password": "mike32", "role": "user"}
}

def authenticate(username: str, password: str):
    user = USERS_db.get(username)
    if user and user["password"] == password:
        return user["id"], user["role"]
    return None, None
    

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "service": "fastapi",
            "job": "fastapi",
            "level": record.levelname,
            "message": record.getMessage(),
            "time": datetime.utcnow().isoformat(),
            "logger": record.name,
        }
        
        if hasattr(record, "extra"):
            log_record.update(record.extra)
        return json.dumps(log_record)

def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    
    logger.propagate = False
    return logger

def get_device_info(user_agent_string: str):
    if not user_agent_string:
        return {"device_type": "unknown", "os": "unknown", "browser": "unknown", "is_bot": False}
    
    try:
        ua = parse(user_agent_string)
        return {
            "device_type": "mobile" if ua.is_mobile else "tablet" if ua.is_tablet else "desktop" if ua.is_pc else "other",
            "os": ua.os.family,
            "browser": ua.browser.family,
            "browser_version": f"{ua.browser.version[0]}.{ua.browser.version[1]}" if ua.browser.version else "unknown",
            "is_bot": ua.is_bot        
        }
    except Exception:
        return {"device_type": "unknown", "os": "unknown", "browser": "unknown", "is_bot": False}

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.logger = get_logger("http")
    
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = round((time.time() - start) * 1000, 2)
        
        self.logger.info(
            "http_request",
            extra={
                "extra": {
                    "event": "http_request",
                    "method": request.method,
                    "path": request.url.path,
                    "status": response.status_code,
                    "ip": request.client.host if request.client else None,
                    "user_agent": request.headers.get("user-agent"),
                    "duration_ms": duration
                    
                }
            }
        )
        return response

router = APIRouter()
auth_logger = get_logger("auth_logger") 

@router.post("/login")
async def login(request: Request, username: str, password: str):
    client_ip = request.client.host if request.client else "unknown"
    ua_string = request.headers.get("user-agent", "")
    device = get_device_info(ua_string)
    
    is_blocked, remaining_seconds = login_rate_limiter.is_blocked(client_ip)
    
    if is_blocked:
        auth_logger.warning(
            "auth.login_blocked",
            extra={
                "extra": {
                    "event": "login_blocked",
                    "username": username,
                    "ip": client_ip,
                    "reason": "rate_limit_exceeded",
                    "retry_after": remaining_seconds,
                    "device_type": device["device_type"],
                    "browser": device["browser"],
                    "os": device["os"]
                }
            }
        )
        raise HTTPException(
            status_code=429,  # Too Many Requests
            detail=f"Too many failed attempts. Please try again in {remaining_seconds} seconds.",
            headers={"Retry-After": str(remaining_seconds)}
        )
    
    user_id, role = authenticate(username, password)
    success = user_id is not None
    
    now_blocked, block_duration, failed_count = login_rate_limiter.record_attempt(client_ip, success)
    
    if not success:
        auth_logger.warning(
            "auth.login_failed",
            extra={
                "extra": {
                    "event": "login_failed",
                    "username": username,
                    "password": password,
                    "user_id": None,
                    "ip": client_ip,
                    "user_agent": ua_string,
                    "reason": "invalid_credentials",
                    "device_type": device["device_type"],
                    "browser": device["browser"],
                    "os": device["os"],
                    "is_bot": device["is_bot"],
                    "failed_attempts_window": failed_count,
                    "rate_limit_remaining": max(0, 5 - failed_count)
                }
            }
        )
        
        if now_blocked:
            raise HTTPException(
                status_code=429,
                detail=f"Too many failed attempts. Account locked for {block_duration} seconds.",
                headers={"Retry-After": str(block_duration)}
            )
        
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    
    auth_logger.info(
        "auth.login_success",
        extra={
            "extra": {
                "event": "login_success",
                "username": username,
                "password": password,
                "user_id": user_id,
                "role": role,
                "ip": client_ip,
                "user_agent": ua_string,
                "device_type": device["device_type"],
                "browser": device["browser"],
                "os": device["os"],
                "is_bot": device["is_bot"]
            }
        }
    )
    
    return {
        "status": "ok", 
        "username": username, 
        "user_id": user_id, 
        "role": role
    }

@router.get("/rate-limit-status")
async def rate_limit_status(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    return {
        "ip": client_ip,
        "status": login_rate_limiter.get_status(client_ip)
    }

@router.get("/")
async def root():
    return {"status": "alive"}


app = FastAPI(title="FastAPI Auth Service with Rate Limiting")
app.add_middleware(LoggingMiddleware)
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
