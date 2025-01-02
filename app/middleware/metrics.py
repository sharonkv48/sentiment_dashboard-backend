from fastapi import Request
from prometheus_client import Counter, Histogram
import time
from loguru import logger

# Metrics
REQUESTS = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
RESPONSES = Counter('http_responses_total', 'Total HTTP responses', ['method', 'endpoint', 'status'])
LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    try:
        response = await call_next(request)
        
        # Record metrics
        duration = time.time() - start_time
        REQUESTS.labels(method=request.method, endpoint=request.url.path).inc()
        RESPONSES.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        LATENCY.observe(duration)
        
        # Log request details
        logger.info(f"{request.method} {request.url.path} {response.status_code} {duration:.2f}s")
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Request failed: {str(e)}")
        RESPONSES.labels(method=request.method, endpoint=request.url.path, status=500).inc()
        raise