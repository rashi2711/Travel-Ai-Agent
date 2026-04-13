# TravelMind AI 🌍✈️

> **An AI-powered full-stack travel platform with production-grade infrastructure**
> Python · Streamlit · MongoDB · OpenAI · Gemini · Docker · Kubernetes · Prometheus · Grafana · GitHub Actions

[![CI/CD](https://img.shields.io/github/actions/workflow/status/rashi2711/travelmind-ai/ci-cd.yml?label=CI%2FCD&logo=github)](https://github.com/rashi2711/travelmind-ai/actions)
[![Docker](https://img.shields.io/badge/Docker-containerized-2496ED?logo=docker)](https://hub.docker.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-deployed-326CE5?logo=kubernetes)](https://kubernetes.io)
[![Monitoring](https://img.shields.io/badge/Monitoring-Prometheus%20%2B%20Grafana-orange?logo=grafana)](http://localhost:3001)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-deployed-FF4B4B?logo=streamlit)](https://streamlit.io)

---

## 📋 Table of Contents

- [About the Project](#-about-the-project)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Docker Setup](#-docker-setup)
- [Observability Stack](#-observability-stack-prometheus--grafana)
- [Kubernetes Deployment](#-kubernetes-deployment-minikube)
- [CI/CD Pipeline](#-cicd-pipeline-github-actions)
- [Health Monitoring](#-health-monitoring)
- [Project Structure](#-project-structure)
- [Resume Highlights](#-resume-highlights)
- [Author](#-author)

---

## 🧠 About the Project

TravelMind AI is a production-grade full-stack AI travel platform that combines intelligent conversation with real-time analytics. Built with a multi-provider LLM architecture (GPT-4o-mini + Gemini 1.5-flash), it provides personalised travel recommendations while tracking business metrics through interactive dashboards.

What makes this project stand out is not just the application — it is the **complete SRE and DevOps infrastructure** built around it: containerisation, orchestration, observability, CI/CD automation, and health monitoring — the same stack used by engineering teams at scale.

**Live Demo:** [travelmind.streamlit.app](https://travelai.streamlit.app)
**GitHub:** [github.com/rashi2711](https://github.com/rashi2711)

---

## ✨ Features

### Application Features
- 🤖 **Multi-provider AI** — GPT-4o-mini and Gemini 1.5-flash with zero vendor lock-in
- 💬 **Context-aware conversations** — per-user chat history with multi-turn memory
- 📊 **6 interactive dashboards** — GMV, CAC, revenue, conversion rates, filterable by date/channel/vertical
- 🔐 **Secure auth** — bcrypt password hashing, session management
- 🗄️ **Resilient database** — MongoDB Atlas with in-memory fallback
- 📱 **Responsive UI** — works across desktop and mobile

### Infrastructure Features
- 🐳 **Dockerised** — containerised app with docker-compose orchestration
- ☸️ **Kubernetes** — 2-replica HA deployment with liveness/readiness probes
- 📈 **Prometheus + Grafana** — real-time metrics and observability dashboards
- 🔄 **GitHub Actions CI/CD** — automated lint, build, and Docker Hub push on every commit
- 🩺 **Health monitoring** — Bash script polling every 30s with alert threshold logic

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Streamlit, Python, Plotly, HTML/CSS |
| **Backend** | Python, REST APIs, Modular architecture (ai/ · database/ · utils/) |
| **Database** | MongoDB Atlas, In-memory fallback |
| **AI/LLM** | OpenAI GPT-4o-mini, Google Gemini 1.5-flash |
| **Containerisation** | Docker, Docker Compose |
| **Orchestration** | Kubernetes (Minikube), kubectl |
| **Observability** | Prometheus, Grafana |
| **CI/CD** | GitHub Actions |
| **Auth** | bcrypt, Session management |
| **Deployment** | Streamlit Cloud, Docker Hub |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub Actions CI/CD                  │
│         Lint → Build Docker Image → Push to Hub         │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              Kubernetes Cluster (Minikube)               │
│   ┌─────────────┐    ┌─────────────┐                    │
│   │  Pod 1      │    │  Pod 2      │  ← 2 replicas HA   │
│   │ TravelMind  │    │ TravelMind  │                     │
│   └──────┬──────┘    └──────┬──────┘                    │
│          └────────┬─────────┘                            │
│          ┌────────▼──────────┐                           │
│          │  travelmind-svc   │  LoadBalancer             │
│          └────────┬──────────┘                           │
└───────────────────┼─────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────┐
│                 Application Layer                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │  ai/     │  │database/ │  │      utils/          │  │
│  │ GPT-4o   │  │ MongoDB  │  │  Auth · Analytics    │  │
│  │ Gemini   │  │ Atlas    │  │  Session Management  │  │
│  └──────────┘  └──────────┘  └──────────────────────┘  │
└──────────────────────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────┐
│              Observability Stack                         │
│   Prometheus (metrics) → Grafana (dashboards)           │
│   Health Check Script (every 30s polling)               │
└──────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- MongoDB Atlas account (free tier works)
- OpenAI API key OR Google Gemini API key

### Run Locally (without Docker)

```bash
# 1. Clone the repository
git clone https://github.com/rashi2711/travelmind-ai.git
cd travelmind-ai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate          # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Edit .env with your API keys and MongoDB URI

# 5. Run the app
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

**Demo credentials:** `demo` / `demo123`

---

## 🐳 Docker Setup

### Install Docker
Download from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop) (free)

### Build and Run

```bash
# Build the image
docker build -t travelmind:latest .

# Run with environment variables
docker run -p 8501:8501 --env-file .env travelmind:latest
```

Open [http://localhost:8501](http://localhost:8501) — same app, now containerised.

### What the Dockerfile does
- Uses Python 3.11 slim base image
- Copies requirements and installs dependencies
- Exposes port 8501
- Runs Streamlit on container startup

---

## 📈 Observability Stack (Prometheus + Grafana)

### Run the full stack

```bash
# Starts TravelMind + Prometheus + Grafana together
docker compose up --build
```

| Service | URL | Login |
|---------|-----|-------|
| TravelMind | http://localhost:8501 | demo / demo123 |
| Prometheus | http://localhost:9090 | no login needed |
| Grafana | http://localhost:3001 | admin / admin |

### Setting up Grafana Dashboard

1. Go to [http://localhost:3001](http://localhost:3001)
2. Login: `admin` / `admin`
3. Click **Dashboards** → **New** → **Import**
4. Enter Dashboard ID: `1860` (Node Exporter Full)
5. Click **Load** → **Import**

You will see real-time system metrics including CPU, memory, and network usage.

### What Prometheus monitors
- Application health endpoint (`/healthz`)
- Container resource usage (CPU, memory)
- Request rate and response times
- Error rate tracking

---

## ☸️ Kubernetes Deployment (Minikube)

### Install Minikube

```bash
# macOS
brew install minikube

# Windows (PowerShell as Admin)
winget install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

### Deploy TravelMind to Kubernetes

```bash
# 1. Start local cluster
minikube start

# 2. Point Docker to Minikube's registry
eval $(minikube docker-env)            # macOS/Linux
minikube docker-env | Invoke-Expression # Windows PowerShell

# 3. Build image inside Minikube
docker build -t travelmind:latest .

# 4. Deploy to cluster
kubectl apply -f deployment.yaml

# 5. Check deployment status
kubectl get pods        # Should show 2 pods Running
kubectl get services    # Shows travelmind-service

# 6. Open in browser
minikube service travelmind-service --url
```

### Kubernetes Configuration Highlights
- **2 replicas** — High availability, zero downtime deployments
- **Liveness probe** — Kubernetes restarts unhealthy pods automatically
- **Readiness probe** — Traffic only routes to pods that are ready
- **Resource limits** — CPU and memory capped to prevent runaway usage
- **LoadBalancer service** — External traffic routing

### Useful kubectl Commands

```bash
# Debug a specific pod
kubectl describe pod <pod-name>

# View application logs
kubectl logs <pod-name>

# Scale up to 3 replicas
kubectl scale deployment travelmind --replicas=3

# Scale down
kubectl scale deployment travelmind --replicas=1

# Tear down everything
kubectl delete -f deployment.yaml

# Check resource usage
kubectl top pods
```

---

## 🔄 CI/CD Pipeline (GitHub Actions)

Every push to `main` branch automatically:

1. **Lint** — runs `flake8` on all Python files
2. **Build** — builds Docker image if lint passes
3. **Push** — pushes image to Docker Hub with commit SHA tag

### Setup (one time)

```
GitHub repo → Settings → Secrets and variables → Actions
```

Add these secrets:

| Secret | Value |
|--------|-------|
| `DOCKER_USERNAME` | Your Docker Hub username |
| `DOCKER_PASSWORD` | Your Docker Hub password or access token |

### Verify CI/CD is working

Go to your repo → **Actions** tab → green ✓ means pipeline passed.

Each successful build creates a Docker image tagged with the commit SHA — enabling rollback to any previous version.

---

## 🩺 Health Monitoring

A Bash script monitors the application endpoint every 30 seconds and alerts after 3 consecutive failures.

```bash
# Make executable (one time)
chmod +x health-check.sh

# Run the monitor
./health-check.sh
```

Logs are written to `health-check.log`. The script:
- Polls `http://localhost:8501/healthz` every 30 seconds
- Logs timestamp + status on every check
- Alerts to console after 3 consecutive failures
- Resets failure counter on successful response

This simulates SRE-style automated incident detection.

---

## 📁 Project Structure

```
travelmind-ai/
├── app.py                          ← Main Streamlit application
├── requirements.txt                ← Python dependencies
├── .env.example                    ← Environment variables template
│
├── ai/                             ← LLM integration module
│   ├── openai_client.py            ← GPT-4o-mini provider
│   └── gemini_client.py            ← Gemini 1.5-flash provider
│
├── database/                       ← Database layer
│   ├── mongo_client.py             ← MongoDB Atlas connection
│   └── memory_store.py             ← In-memory fallback
│
├── utils/                          ← Utilities
│   ├── auth.py                     ← bcrypt authentication
│   ├── analytics.py                ← Dashboard data processing
│   └── session.py                  ← User session management
│
├── Dockerfile                      ← Container definition
├── .dockerignore                   ← Docker build exclusions
├── docker-compose.yml              ← Multi-service orchestration
├── deployment.yaml                 ← Kubernetes manifests
├── prometheus.yml                  ← Prometheus scrape config
├── health-check.sh                 ← SRE health monitor script
│
├── grafana/
│   └── provisioning/
│       └── datasources/
│           └── prometheus.yml      ← Grafana auto-configuration
│
└── .github/
    └── workflows/
        └── ci-cd.yml               ← GitHub Actions pipeline
```

---

## 🌐 Environment Variables

Create a `.env` file in the root directory:

```env
# AI Providers (at least one required)
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Database
MONGODB_URI=your_mongodb_atlas_uri_here

# App Config
APP_SECRET_KEY=your_random_secret_key_here
DEFAULT_LLM_PROVIDER=gemini         # or openai
```

> **Note:** Never commit your `.env` file. It is already in `.gitignore`.

---

## 📊 Resume Highlights

This project demonstrates the following skills directly applicable to SDE / DevOps / SRE roles:

**Skills to add to your resume:**
```
Infrastructure & OS: Linux Server, Docker, Kubernetes (Minikube), Microservices Architecture
DevOps / Tools: Git, GitHub, GitHub Actions (CI/CD), Prometheus, Grafana, Postman, VS Code
```

**Project bullets to add:**
```
• Containerised Python/Streamlit app using Docker; deployed via docker-compose with
  Prometheus + Grafana observability stack — tracking app health and response metrics.

• Deployed to local Kubernetes cluster (Minikube) with 2-replica HA setup, liveness/
  readiness probes, and resource limits — production-grade reliability configuration.

• Configured GitHub Actions CI/CD pipeline — automated lint, Docker build, and image
  push to Docker Hub on every commit to main.

• Wrote Bash health-check script polling app endpoint every 30s with alert threshold
  logic — SRE-style automated incident detection.
```

---

## 👩‍💻 Author

**Rashi Garg**
- 📧 rashigarg788@gmail.com
- 🔗 [LinkedIn](https://linkedin.com/in/rashigarg)
- 💻 [GitHub](https://github.com/rashi2711)
- 🌐 [Portfolio](https://rashigarg.dev)

**National Winner — Smart India Hackathon 2024** | B.Tech CSE, LNCTS Bhopal (2026)

---

## 📄 License

MIT License — feel free to use this project as a reference or template.

---

<div align="center">

**If this project helped you, please give it a ⭐ on GitHub!**

*Built with ❤️ and lots of chai by Rashi Garg*

</div>
