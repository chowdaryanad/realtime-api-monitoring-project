"""
RTAM API — Application Entrypoint

Initialises the FastAPI application with Prometheus instrumentation
for real-time metrics collection and monitoring.
"""

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title="RTAM API",
    description="Real-Time API Monitoring & Observability System",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "RTAM API Running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "rtam-api"}


# Prometheus metrics instrumentation
instrumentator = Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    excluded_handlers=["/health", "/metrics"],
)
instrumentator.instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)