<div align="center">

# 🔍 Real-Time API Monitoring & Observability System

**Production-grade API monitoring stack built with FastAPI, Prometheus, Grafana, Loki, and Alertmanager**

[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Prometheus](https://img.shields.io/badge/Prometheus-v2.51-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-10.4-F46800?style=for-the-badge&logo=grafana&logoColor=white)](https://grafana.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

</div>

---

## 📐 Architecture

```
                         ┌──────────────────────────────────────────────────┐
                         │              Monitoring Network                 │
                         │                                                 │
┌─────────────┐          │   ┌──────────────┐       ┌──────────────────┐   │
│             │  /metrics │   │  Prometheus  │──────▶│  Alertmanager    │   │
│   FastAPI   │──────────────▶│  :9090       │       │  :9093           │   │
│   :8000     │          │   └──────┬───────┘       └──────────────────┘   │
│             │          │          │                                       │
└──────┬──────┘          │          ▼                                       │
       │                 │   ┌──────────────┐                              │
       │   logs          │   │   Grafana    │◀── Dashboards (auto-provisioned)
       │                 │   │   :3000      │                              │
       ▼                 │   └──────────────┘                              │
┌──────────────┐         │          ▲                                       │
│  Promtail    │────────────▶┌─────┴────────┐                              │
│  (log agent) │         │   │    Loki      │                              │
└──────────────┘         │   │    :3100     │                              │
                         │   └──────────────┘                              │
┌──────────────┐         │                                                 │
│  PostgreSQL  │         └──────────────────────────────────────────────────┘
│  :5432       │
└──────────────┘
```

**Data Flow:**
1. **FastAPI** exposes `/metrics` endpoint → **Prometheus** scrapes every 10s
2. **Prometheus** evaluates alert rules → fires alerts to **Alertmanager**
3. **Promtail** collects container + application logs → ships to **Loki**
4. **Grafana** queries Prometheus (metrics) + Loki (logs) → unified dashboards

---

## ⚡ Features

| Category | Feature | Details |
|----------|---------|---------|
| 📊 **Metrics** | Request rate monitoring | Track requests/sec across all endpoints |
| 📊 **Metrics** | Latency percentiles | P50, P90, P95, P99 response times |
| 📊 **Metrics** | Status code tracking | Breakdowns by 2xx, 4xx, 5xx |
| 🚨 **Alerting** | API down detection | Fires within 1 min of downtime |
| 🚨 **Alerting** | High error rate (>5%) | Critical alert on 5xx spike |
| 🚨 **Alerting** | Latency threshold | Warning when p95 > 1 second |
| 🚨 **Alerting** | Memory threshold | Warning when RSS > 512 MB |
| 📝 **Logging** | Structured JSON logs | Via structlog + python-json-logger |
| 📝 **Logging** | Centralized aggregation | Loki + Promtail pipeline |
| 📈 **Dashboards** | Auto-provisioned | Zero-config Grafana dashboards on startup |
| 🐳 **Infra** | Full Docker Compose | One-command deployment |
| 🐳 **Infra** | Health checks | All services include readiness probes |

---

## 🛠️ Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **API Framework** | FastAPI + Uvicorn | 0.111 |
| **Database** | PostgreSQL (Alpine) | 16 |
| **Metrics** | Prometheus | 2.51 |
| **Visualization** | Grafana | 10.4 |
| **Alerting** | Alertmanager | 0.27 |
| **Log Aggregation** | Loki | 2.9.6 |
| **Log Shipping** | Promtail | 2.9.6 |
| **Language** | Python | 3.12 |
| **Containerization** | Docker Compose | v2 |

---

## 🚀 Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/) v2+
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/chowdaryanad/realtime-api-monitoring-project.git
cd realtime-api-monitoring-project
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env → set POSTGRES_PASSWORD and GF_ADMIN_PASSWORD
```

### 3. Launch the Stack

```bash
docker compose up --build -d
```

### 4. Verify Services

```bash
# API health check
curl http://localhost:8000/health
# → {"status":"healthy","service":"rtam-api"}

# Prometheus targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[].health'
```

---

## 🌐 Access URLs

| Service | URL | Default Credentials |
|---------|-----|-------------------|
| **API** | [http://localhost:8000](http://localhost:8000) | — |
| **API Docs (Swagger)** | [http://localhost:8000/docs](http://localhost:8000/docs) | — |
| **Prometheus** | [http://localhost:9090](http://localhost:9090) | — |
| **Grafana** | [http://localhost:3000](http://localhost:3000) | `admin` / `admin` |
| **Alertmanager** | [http://localhost:9093](http://localhost:9093) | — |
| **Loki** | [http://localhost:3100](http://localhost:3100) | — |

---

## 📂 Project Structure

```
realtime-api-monitoring-project/
│
├── app/                                  # FastAPI Application
│   ├── Dockerfile                        # Multi-stage Python 3.12 image
│   ├── main.py                           # App entrypoint with Prometheus instrumentation
│   ├── requirements.txt                  # Python dependencies (container)
│   └── app/
│       ├── api/v1/endpoints/             # REST route handlers
│       ├── core/                         # Config, middleware, metrics, logging
│       ├── db/                           # SQLAlchemy async engine & sessions
│       ├── models/                       # ORM models
│       ├── schemas/                      # Pydantic request/response schemas
│       └── services/                     # Business logic layer
│
├── monitoring/
│   ├── prometheus/
│   │   ├── prometheus.yml                # Scrape config (API, Loki, self)
│   │   └── alert_rules.yml              # 7 production alert rules
│   ├── alertmanager/
│   │   └── alertmanager.yml             # Routing & receiver config
│   ├── grafana/
│   │   ├── provisioning/
│   │   │   ├── datasources/             # Auto-provisioned: Prometheus, Loki, Alertmanager
│   │   │   └── dashboards/              # Dashboard file provider config
│   │   └── dashboards/
│   │       └── api-overview.json        # Pre-built API monitoring dashboard
│   ├── loki/
│   │   └── loki.yml                     # TSDB storage, 14-day retention
│   └── promtail/
│       └── promtail.yml                 # Docker + file log scraping
│
├── tests/                               # Test suite (pytest)
├── docker-compose.yml                   # Full stack orchestration (8 services)
├── .env.example                         # Environment variable template
├── .gitignore                           # Comprehensive ignore rules
├── requirements.txt                     # Dev/CI dependencies
└── README.md
```

---

## 📊 Example Prometheus Queries

```promql
# Request rate (req/s)
sum(rate(http_requests_total{job="rtam-api"}[1m]))

# P95 response latency
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job="rtam-api"}[5m])) by (le))

# 5xx error rate (%)
sum(rate(http_requests_total{job="rtam-api", status=~"5.."}[5m]))
/ sum(rate(http_requests_total{job="rtam-api"}[5m])) * 100

# API uptime status
up{job="rtam-api"}

# Memory usage (MB)
process_resident_memory_bytes{job="rtam-api"} / 1024 / 1024

# Total requests by endpoint
sum by (handler) (rate(http_requests_total{job="rtam-api"}[5m]))
```

---

## 🚨 Alert Rules

| Alert | Condition | Severity | Duration |
|-------|-----------|----------|----------|
| `APIDown` | `up{job="rtam-api"} == 0` | 🔴 Critical | 1 min |
| `APIHighErrorRate` | 5xx rate > 5% | 🔴 Critical | 2 min |
| `APIHighLatency` | P95 > 1 second | 🟡 Warning | 2 min |
| `HighRequestRate` | > 5 req/s (1m avg) | 🟡 Warning | 1 min |
| `HighErrorRate` | Any 4xx errors | 🟡 Warning | 1 min |
| `HighMemoryUsage` | RSS > 512 MB | 🟡 Warning | 5 min |
| `PrometheusTargetDown` | Any target unreachable | 🟡 Warning | 3 min |

---

## 🧪 Development

```bash
# Install dependencies locally
pip install -r requirements.txt

# Run API without Docker
cd app && uvicorn main:app --reload --port 8000

# Run tests
pytest tests/ -v

# Lint code
ruff check app/
```

---

## 🔮 Future Improvements

- [ ] **Slack / PagerDuty integration** — Wire Alertmanager receivers to real notification channels
- [ ] **PostgreSQL Exporter** — Add `postgres-exporter` for database-level metrics (connections, query performance)
- [ ] **Distributed tracing** — Integrate OpenTelemetry + Jaeger/Tempo for end-to-end request tracing
- [ ] **Custom business metrics** — Track domain-specific KPIs (API monitor success rate, uptime SLA)
- [ ] **CI/CD pipeline** — GitHub Actions for automated testing, linting, and image builds
- [ ] **Kubernetes migration** — Helm charts for k8s deployment with HPA and PDB
- [ ] **SSL/TLS** — Nginx reverse proxy with Let's Encrypt certificates
- [ ] **Rate limiting** — Per-client request throttling with Redis-backed middleware
- [ ] **Grafana alerts** — Unified alerting from Grafana with multi-channel notifications
- [ ] **Load testing suite** — Automated k6 / Locust scripts for performance benchmarking

---

## 📝 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

**Built with ❤️ for Production-Grade Observability**

[⬆ Back to Top](#-real-time-api-monitoring--observability-system)

</div>
