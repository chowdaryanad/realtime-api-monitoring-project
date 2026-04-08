"""
Application middleware configuration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.metrics import http_requests_total


class MetricsMiddleware(BaseHTTPMiddleware):
    """Increment http_requests_total for every HTTP request."""

    async def dispatch(self, request, call_next):
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            status_code = 500
            raise
        finally:
            http_requests_total.labels(
                method=request.method,
                handler=request.url.path,
                status=f"{status_code // 100}xx",
            ).inc()

        return response


def setup_middleware(app: FastAPI) -> None:
    """Register all middleware layers."""

    # Prometheus metrics
    app.add_middleware(MetricsMiddleware)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Trusted Host
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],  # TODO: restrict in production
    )
