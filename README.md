# ✈️ TravelMind AI — Travel Assistant + Business Analytics Dashboard

A production-grade full-stack AI application built with Streamlit, MongoDB, and OpenAI/Gemini —
with a complete SRE stack: Docker, Kubernetes, Prometheus, Grafana, and GitHub Actions CI/CD.

---

## 🏗️ Project Structure

```
Travel-Ai-Agent/
├── app.py                          ← Main entry point
├── requirements.txt                ← Python dependencies
├── Dockerfile                      ← Container image
├── .dockerignore
├── docker-compose.yml              ← App + Prometheus + Grafana
├── prometheus.yml                  ← Metrics scrape config
├── deployment.yaml                 ← Kubernetes manifests
├── health-check.sh                 ← SRE health monitor script
│
├── grafana/
│   └── provisioning/
│       └── datasources/
│           └── prometheus.yml      ← Auto-loads Prometheus in Grafana
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml               ← GitHub Actions pipeline
│
├── ai/
│   ├── llm.py                      ← Unified LLM client (OpenAI / Gemini / Demo)
│   └── itinerary.py                ← Itinerary generator, dynamic pricing
│
├── database/
│   ├── connection.py               ← MongoDB + in-memory fallback
│   ├── users.py                    ← Auth (bcrypt)
│   ├── chats.py                    ← Per-user chat history
│   └── bookings.py                 ← 800-row mock data + query helpers
│
└── utils/
    ├── ui.py                       ← Dark luxury CSS + UI components
    └── charts.py                   ← 6 Plotly chart types
```

---

## 🚀 Quick Start (Local)

```bash
git clone https://github.com/rashi2711/Travel-Ai-Agent.git
cd Travel-Ai-Agent
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Add your API keys
streamlit run app.py
```

Open: **http://localhost:8501** | Demo login: `demo` / `demo123`

---

## 🐳 Docker

### Build & Run

```bash
docker build -t travelmind:latest .
docker run -p 8501:8501 --env-file .env travelmind:latest
```

### Run with full observability stack (Prometheus + Grafana)

```bash
docker compose up --build
```

| Service    | URL                      | Credentials   |
|------------|--------------------------|---------------|
| TravelMind | http://localhost:8501    | demo / demo123|
| Prometheus | http://localhost:9090    | —             |
| Grafana    | http://localhost:3001    | admin / admin |

---

## 📊 Observability — Prometheus + Grafana

The `docker-compose.yml` spins up a full monitoring stack alongside the app.

- **Prometheus** scrapes the Streamlit health endpoint every 15s
- **Grafana** auto-connects to Prometheus as a data source
- Import Dashboard ID **1860** in Grafana for system-level metrics

![Grafana Dashboard](docs/grafana-screenshot.png)

---

## ☸️ Kubernetes (Minikube)

```bash
# Start local cluster
minikube start

# Point Docker to Minikube
eval $(minikube docker-env)

# Build image inside Minikube
docker build -t travelmind:latest .

# Deploy (2 replicas, liveness + readiness probes)
kubectl apply -f deployment.yaml

# Check pods
kubectl get pods
kubectl get services

# Open in browser
minikube service travelmind-service --url
```

Features of the K8s setup:
- **2 replicas** for high availability
- **Liveness probe** — restarts pod if app hangs
- **Readiness probe** — holds traffic until app is ready
- **Resource limits** — memory 512Mi, CPU 500m
- **Secrets** — API keys stored as K8s Secrets

---

## ⚙️ CI/CD — GitHub Actions

Every push to `main` triggers:

1. **Lint** — flake8 checks Python syntax and style
2. **Build** — Docker image built
3. **Push** — Image pushed to Docker Hub with commit SHA tag

Setup: Add `DOCKER_USERNAME` and `DOCKER_PASSWORD` in repo → Settings → Secrets.

[![CI/CD](https://github.com/rashi2711/Travel-Ai-Agent/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/rashi2711/Travel-Ai-Agent/actions)

---

## 🩺 Health Monitor (Shell Script)

SRE-style automated health check — polls the app every 30s and alerts on 3 consecutive failures.

```bash
chmod +x health-check.sh
./health-check.sh
```

Sample output:
```
[2025-01-01 10:00:00] Starting TravelMind health monitor
[2025-01-01 10:00:00] ✓ OK  status=200  response_time=0.12s
[2025-01-01 10:00:30] ✓ OK  status=200  response_time=0.09s
[2025-01-01 10:01:00] ✗ FAIL  status=000  consecutive_failures=1
[2025-01-01 10:02:00] 🚨 ALERT — TravelMind down for 3 consecutive checks!
```

---

## 🤖 AI Providers

| Provider | Key | Cost |
|----------|-----|------|
| Demo mode | None needed | Free |
| OpenAI GPT-4o-mini | `OPENAI_API_KEY` | ~$0.01–0.05/itinerary |
| Google Gemini 1.5-flash | `GEMINI_API_KEY` | Free tier (60 req/min) |

Set `AI_PROVIDER=openai` or `gemini` or `demo` in `.env`.

---

## 🗄️ Database

| Mode | Setup | Notes |
|------|-------|-------|
| In-memory (default) | Nothing needed | Resets on restart |
| Local MongoDB | `mongod --dbpath /data/db` | Persistent |
| MongoDB Atlas | Connection string in `.env` | Cloud, free tier |

---

## 📊 Analytics Dashboard

- **KPIs:** GMV · Revenue · Bookings · Conversion Rate · CAC · Repeat Customers
- **6 Charts:** Monthly trend · Channel performance · Conversion by vertical · Revenue heatmap · CAC scatter · Destination popularity
- **Filters:** Date range · Channel · Vertical
- **Dataset:** 800-row realistic mock data (auto-seeded)

---

## 🏗️ Architecture

| Layer | Choice | Reason |
|-------|--------|--------|
| UI | Streamlit | Python-native, rapid prototyping |
| AI | Multi-provider (OpenAI/Gemini/Demo) | Zero vendor lock-in |
| Database | MongoDB + in-memory fallback | Graceful degradation |
| Auth | bcrypt + SHA-256 fallback | Secure, portable |
| Charts | Plotly | Interactive, dark theme |
| Containers | Docker + Kubernetes | Production-grade deployment |
| Monitoring | Prometheus + Grafana | SRE observability stack |
| CI/CD | GitHub Actions | Automated build and push |

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| MongoDB connection fails | App auto-falls back to in-memory |
| OpenAI rate limit | Switch to `AI_PROVIDER=gemini` or `demo` |
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| Docker build fails | Ensure `.env` exists; check `.dockerignore` |
| Minikube pods crash | Run `kubectl logs <pod-name>` to debug |
| Grafana no data | Confirm Prometheus target is UP at `localhost:9090/targets` |

---

## 📄 License

MIT — Free to use, modify, and distribute.