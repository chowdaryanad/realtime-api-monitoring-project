"""
RTAM API — Application Entrypoint

Initialises the FastAPI application with Prometheus instrumentation
for real-time metrics collection and monitoring.
"""

from fastapi import FastAPI, Response
from prometheus_client import generate_latest

from app.core.middleware import setup_middleware

app = FastAPI(
    title="RTAM API",
    description="Real-Time API Monitoring & Observability System",
    version="1.0.0",
)

@app.get("/crash")
def crash():
    raise Exception("Simulated failure")  #this is lastly modified

@app.get("/")
def root():
    return {"message": "RTAM API Running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "rtam-api"}


@app.get("/metrics", include_in_schema=False)
def metrics():
    """Expose Prometheus metrics."""
    return Response(generate_latest(), media_type="text/plain")


# Register all middleware (metrics, CORS, trusted-host)
setup_middleware(app)