<div align="center">

# Real-Time API Monitoring & Observability System

**A production-grade observability stack that instruments a FastAPI application with custom Prometheus metrics, automated Grafana dashboards, and email-based alerting — deployed as a single Docker Compose command.**

[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Prometheus](https://img.shields.io/badge/Prometheus-v2.51-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-10.4-F46800?style=for-the-badge&logo=grafana&logoColor=white)](https://grafana.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

</div>

---

## Overview

This project implements a complete monitoring pipeline for a REST API — from metric instrumentation at the application layer, through collection and storage in Prometheus, to visualization in Grafana and automated alerting via email.

The system is designed around a single custom metric, `http_requests_total`, recorded through a hand-written Starlette middleware rather than a third-party auto-instrumentator. This gives full control over label cardinality and ensures every request — including unhandled exceptions that result in 5xx responses — is accurately captured.

**What makes this different from a tutorial project:**
- Metrics middleware uses `try/except/finally` to guarantee counter increments even on server errors
- Alert rules use `increase()` instead of `rate()` to fire reliably in low-traffic environments
- Grafana dashboards are auto-provisioned on container startup with no manual import steps
- Alertmanager delivers real email notifications (FIRING and RESOLVED) via Gmail SMTP
- All 8 services include health checks, restart policies, and structured logging

---

## Architecture

```
                         ┌──────────────────────────────────────────────────┐
                         │              Monitoring Network                 │
                         │                                                 │
┌─────────────┐          │   ┌──────────────┐       ┌──────────────────┐   │
│             │  /metrics │   │  Prometheus  │──────>│  Alertmanager    │   │
│   FastAPI   │──────────────>│  :9090       │       │  :9093           │   │
│   :8000     │          │   └──────┬───────┘       └────────┬─────────┘   │
│             │          │          │                         │             │
└──────┬──────┘          │          v                    Email (SMTP)       │
       │                 │   ┌──────────────┐                              │
       │   logs          │   │   Grafana    │<── Dashboards (provisioned)  │
       │                 │   │   :3000      │                              │
       v                 │   └──────────────┘                              │
┌──────────────┐         │          ^                                      │
│  Promtail    │────────────>┌─────┴────────┐                              │
│  (log agent) │         │   │    Loki      │                              │
└──────────────┘         │   │    :3100     │                              │
                         │   └──────────────┘                              │
┌──────────────┐         │                                                 │
│  PostgreSQL  │         └─────────────────────────────────────────────────┘
│  :5432       │
└──────────────┘
```

**Data flow:**
1. Every HTTP request passes through `MetricsMiddleware`, which increments `http_requests_total` with `method`, `handler`, and `status` labels
2. Prometheus scrapes the `/metrics` endpoint every 10 seconds and evaluates alert rules
3. When an alert fires, Prometheus pushes it to Alertmanager, which sends an email via Gmail SMTP
4. Grafana queries Prometheus for dashboard panels — auto-provisioned on startup, no manual setup

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Application** | FastAPI 0.111 + Uvicorn | Async Python API with `/health`, `/crash`, `/metrics` endpoints |
| **Database** | PostgreSQL 16 (Alpine) | Persistent data store |
| **Metrics** | prometheus-client + custom middleware | `http_requests_total` counter with method/handler/status labels |
| **Collection** | Prometheus 2.51 | Scraping, storage (15d retention), alert rule evaluation |
| **Visualization** | Grafana 10.4 | Auto-provisioned dashboards with stat, time series, bar, and pie panels |
| **Alerting** | Alertmanager 0.27 | Email notifications via Gmail SMTP with severity-based routing |
| **Logging** | Loki 2.9.6 + Promtail | Centralized log aggregation from containers and application logs |
| **Orchestration** | Docker Compose v2 | Single-command deployment of all 8 services |

---

## Features

### Instrumentation

- **Custom metrics middleware** — Hand-written `BaseHTTPMiddleware` subclass that records every request, not a black-box auto-instrumentator
- **Exception-safe counting** — `try/except/finally` pattern ensures 5xx errors from unhandled exceptions are always recorded
- **Singleton counter** — `http_requests_total` defined once in `app/core/metrics.py`, imported wherever needed, preventing duplicate registration errors
- **Status code bucketing** — Responses grouped as `2xx`, `4xx`, `5xx` for clean aggregation in dashboards and alert rules

### Dashboards (Grafana)

Two auto-provisioned dashboards on startup:

| Panel | Type | Query |
|-------|------|-------|
| Total Requests | Stat | `sum(http_requests_total)` |
| Request Rate (RPS) | Stat | `sum(rate(http_requests_total[1m]))` |
| Error Rate (4xx) | Stat | `sum(rate(http_requests_total{status=~"4.."}[1m]))` |
| API Status (UP/DOWN) | Stat | `up{job="rtam-api"}` |
| Request Rate — Time Series | Time series | `rate(http_requests_total[1m])` by label |
| Requests by Endpoint | Bar chart | `sum by (handler) (http_requests_total)` |
| Status Code Distribution | Donut pie | `sum by (status) (http_requests_total)` |
| 4xx/5xx Error Rate | Time series | Error rates over time with threshold lines |

### Alerting

| Alert | Expression | Severity | Fires After |
|-------|-----------|----------|-------------|
| `APIDown` | `up{job="rtam-api"} == 0` | Critical | 1 min |
| `APIHighErrorRate` | 5xx error ratio > 5% over 5m | Critical | 2 min |
| `HighErrorRate` | `increase(http_requests_total{status=~"4.."}[1m]) > 0` | Critical | 10s |
| `HighServerErrorRate` | `increase(http_requests_total{status=~"5.."}[1m]) > 0` | Critical | 10s |
| `HighTrafficSpike` | `rate(http_requests_total[1m]) > 5` | Warning | 15s |
| `HighRequestRate` | `sum(rate(...[1m])) > 5` | Warning | 1 min |
| `APIHighLatency` | P95 latency > 1 second | Warning | 2 min |
| `HighMemoryUsage` | RSS > 512 MB | Warning | 5 min |
| `PrometheusTargetDown` | Any scrape target unreachable | Warning | 3 min |

**Why `increase()` over `rate()`:** In low-traffic environments, `rate()` returns a per-second average that can hover near zero due to floating-point precision — making `> 0` unreliable. `increase()` returns the actual count of events in the window, so even a single 4xx or 5xx reliably triggers the alert.

### Email Notifications

- FIRING and RESOLVED emails via Gmail SMTP (TLS)
- Severity-based routing: critical alerts repeat every 30 minutes, others every hour
- Inhibition rules: critical alerts suppress corresponding warnings to reduce noise

---

## Setup

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) v2+
- A Gmail account with [App Password](https://myaccount.google.com/apppasswords) (requires 2-Step Verification)

### 1. Clone and configure

```bash
git clone https://github.com/chowdaryanad/realtime-api-monitoring-project.git
cd realtime-api-monitoring-project
cp .env.example .env
# Edit .env — set POSTGRES_PASSWORD and GF_ADMIN_PASSWORD
```

### 2. Configure email alerts (optional)

Edit `monitoring/alertmanager/alertmanager.yml` and replace the SMTP placeholders with your Gmail address and App Password.

### 3. Launch

```bash
docker compose up --build -d
```

### 4. Verify

```bash
# API health
curl http://localhost:8000/health
# {"status":"healthy","service":"rtam-api"}

# Prometheus targets
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[].health'
# "up"
```

### Service URLs

| Service | URL | Credentials |
|---------|-----|------------|
| API | http://localhost:8000 | — |
| API Docs (Swagger) | http://localhost:8000/docs | — |
| Prometheus | http://localhost:9090 | — |
| Grafana | http://localhost:3000 | `admin` / `admin` |
| Alertmanager | http://localhost:9093 | — |

---

## Testing the Observability Pipeline

These endpoints let you generate different status codes and verify that metrics, dashboards, and alerts respond correctly.

```bash
# Generate 2xx — healthy traffic
curl http://localhost:8000/health

# Generate 4xx — triggers HighErrorRate alert
curl http://localhost:8000/invalid-endpoint

# Generate 5xx — triggers HighServerErrorRate alert
curl http://localhost:8000/crash
```

**What to verify after each request:**

1. **Metrics** — `curl http://localhost:8000/metrics | grep http_requests_total` should show incremented counters with correct status labels
2. **Prometheus** — Navigate to Alerts tab at http://localhost:9090/alerts to see FIRING state
3. **Grafana** — Open http://localhost:3000 and check the API Monitoring dashboard for live updates
4. **Email** — After alert fires, check inbox for FIRING notification; after resolution, a RESOLVED email follows

---

## Project Structure

```
realtime-api-monitoring-project/
├── app/
│   ├── Dockerfile
│   ├── main.py                           # App entrypoint — routes + /metrics endpoint
│   ├── requirements.txt
│   └── app/
│       ├── core/
│       │   ├── metrics.py                # http_requests_total Counter (single definition)
│       │   ├── middleware.py             # MetricsMiddleware + CORS + TrustedHost
│       │   ├── config.py
│       │   └── logging.py
│       ├── api/v1/endpoints/
│       ├── db/
│       ├── models/
│       ├── schemas/
│       └── services/
│
├── monitoring/
│   ├── prometheus/
│   │   ├── prometheus.yml                # Scrape config (10s interval for API)
│   │   └── alert_rules.yml              # 9 alert rules across 3 groups
│   ├── alertmanager/
│   │   └── alertmanager.yml             # Gmail SMTP + severity-based routing
│   ├── grafana/
│   │   ├── provisioning/
│   │   │   ├── datasources/             # Prometheus, Loki, Alertmanager
│   │   │   └── dashboards/              # File-based dashboard provider
│   │   └── dashboards/
│   │       ├── api-monitoring.json      # Primary dashboard (8 panels)
│   │       └── api-overview.json        # Secondary overview dashboard
│   ├── loki/
│   │   └── loki.yml
│   └── promtail/
│       └── promtail.yml
│
├── docker-compose.yml                    # 8 services with health checks
├── .env.example
├── .gitignore
└── README.md
```

---

## Key Design Decisions

These are the non-obvious choices that differentiate this from a basic tutorial setup:

| Decision | Rationale |
|----------|-----------|
| **Custom middleware over auto-instrumentator** | `prometheus-fastapi-instrumentator` creates its own metric names and doesn't expose `http_requests_total`. Writing the middleware by hand gives full control over metric naming, label cardinality, and exception handling. |
| **`increase()` in alert rules** | `rate()` returns a per-second float that's unreliable near zero in low-traffic environments. `increase()` returns integer event counts, making `> 0` thresholds deterministic. |
| **`try/except/finally` in middleware** | Without exception handling, any unhandled error skips the counter increment entirely — meaning 5xx responses are invisible to monitoring. The `finally` block guarantees the metric is recorded regardless of outcome. |
| **Singleton counter in `metrics.py`** | Defining the counter in one module and importing it prevents `Duplicated timeseries` registration errors that occur when counters are instantiated in multiple places. |
| **`send_resolved: true` in Alertmanager** | Receiving RESOLVED emails confirms the system is self-healing and provides a complete audit trail of incidents. |
| **Datasource variable in Grafana JSON** | Using `${DS_PROMETHEUS}` instead of a hardcoded datasource UID makes dashboards portable across environments without manual editing. |

---

## Key Learnings

1. **Observability is not monitoring** — Monitoring tells you *when* something breaks; observability tells you *why*. Structured metrics with meaningful labels (`method`, `handler`, `status`) enable root-cause analysis without searching through logs.

2. **Middleware ordering matters** — Starlette processes middleware in reverse registration order. `MetricsMiddleware` must be registered first (via `add_middleware`) so it wraps all other middleware and captures the final response status.

3. **`rate()` vs `increase()` is a real operational decision** — In production, low-traffic services with `rate()` + `> 0` thresholds will produce false negatives. This is a common interview discussion point around PromQL precision.

4. **Infrastructure-as-Code for dashboards** — Manually creating Grafana dashboards is a liability. Provisioning via JSON + volume mounts ensures dashboards are version-controlled, reproducible, and survive container restarts.

5. **Alert fatigue is a design problem** — Inhibition rules (critical suppresses warning for the same alert), `group_by` labels, and tuned `repeat_interval` values prevent duplicate notifications during an incident.

---

## Future Improvements

- [ ] **Distributed tracing** — OpenTelemetry SDK + Jaeger/Tempo for end-to-end request tracing
- [ ] **PostgreSQL Exporter** — Database-level metrics (active connections, query latency, replication lag)
- [ ] **CI/CD pipeline** — GitHub Actions for automated testing, linting, and container image builds
- [ ] **Kubernetes migration** — Helm charts with HPA, PDB, and ServiceMonitor CRDs for Prometheus Operator
- [ ] **Slack / PagerDuty integration** — Additional Alertmanager receivers for team-based routing
- [ ] **Rate limiting** — Redis-backed per-client throttling with metrics exported to Prometheus
- [ ] **Load testing** — k6 or Locust scripts for sustained performance benchmarking under realistic traffic patterns

---

## License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

**Built for production-grade observability**

[Back to Top](#real-time-api-monitoring--observability-system)

</div>
