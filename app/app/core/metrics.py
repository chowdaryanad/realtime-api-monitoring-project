"""
Prometheus metrics instrumentation.
"""

from prometheus_fastapi_instrumentator import Instrumentator


def setup_metrics(app):
    """Attach Prometheus metrics middleware to the FastAPI application.

    IMPORTANT: This must be called AFTER all routes are registered on the app.
    The instrumentator middleware matches requests to route handlers — routes
    added later will not be tracked.
    """
    Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        should_respect_env_var=False,
        excluded_handlers=["/metrics"],
        env_var_name="PROMETHEUS_ENABLED",
    ).instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
