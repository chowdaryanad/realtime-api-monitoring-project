"""
Prometheus metrics definitions.

All application-level metrics are defined here as singletons.
Import from this module wherever you need to record metrics —
never re-define counters/gauges/histograms elsewhere.
"""

from prometheus_client import Counter

http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "handler", "status"],
)
