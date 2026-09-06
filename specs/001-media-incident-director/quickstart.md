# Quickstart & Validation Guide: Studio Guardian

**Feature**: `001-media-incident-director`  
**Target Environment**: Local development & Google Cloud Run  
**Status**: Ready for Implementation  

---

## 1. Prerequisites

- **Python 3.12+**
- **Node.js 20+** & `npm`
- **Docker** & **Docker Compose** (for local PostgreSQL 16 & optional Grafana)
- **Google Cloud SDK (`gcloud`)** authenticated with active project (or `GEMINI_API_KEY` for local testing)

---

## 2. Environment Setup

### 2.1 Clone & Configure Environment
```bash
cp .env.example .env
```

Ensure `.env` contains:
```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/studio_guardian

# Google Cloud / Gemini
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_GENAI_USE_VERTEXAI=true
GEMINI_API_KEY=your-gemini-api-key-if-not-using-adc

# Grafana MCP Integration
GRAFANA_URL=http://localhost:3000
GRAFANA_SERVICE_ACCOUNT_TOKEN=glsa_example_token_123
USE_MOCK_GRAFANA_MCP=true # Set to false when connecting to live Grafana

# Studio Guardian Configuration
PORT=8000
LOG_LEVEL=info
MAX_REMEDIATION_RETRIES=2
```

### 2.2 Start PostgreSQL Infrastructure
```bash
docker compose up -d postgres
```

### 2.3 Backend Setup & Database Migrations
```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
alembic upgrade head
```

### 2.4 Frontend Setup
```bash
cd ../frontend
npm install
```

---

## 3. Running Locally

### Start Backend (Terminal 1)
```bash
cd backend
uvicorn src.main:app --reload --port 8000
```
Backend API will be live at `http://localhost:8000/docs`.

### Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```
Studio Guardian Command Center will be live at `http://localhost:5173`.

---

## 4. End-to-End Validation Scenario

This scenario executes the complete 3-minute reproducible demo required by hackathon judges.

### Step 1: Verify Baseline Health
1. Open `http://localhost:5173`.
2. Observe the central 3D "Live Event Core" displaying **India vs Australia Final** in `HEALTHY` status.
3. Observe baseline playback error rate at **0.4%** across 12.4M concurrent viewers.

### Step 2: Inject Deterministic Incident
Trigger the scenario via the UI button **"Trigger Incident"** or execute via curl:
```bash
curl -X POST http://localhost:8000/api/v1/demo/incident \
  -H "Content-Type: application/json" \
  -d '{"scenario": "india_vs_australia_final"}'
```

**Expected Result**:
- Event status transitions from `HEALTHY` → `DETECTED`.
- 3D globe highlights Australia and Singapore nodes pulsing in amber/red.
- Playback error rate spikes to **8.7%**.

### Step 3: Observe Autonomous Multi-Agent Investigation
- **Incident Commander** activates and coordinates specialists.
- **Observability Investigator** executes `query_prometheus_metrics` and `search_loki_logs` via Grafana MCP, correlating high GPU memory allocation failures and deployment `v4.2.1-transcoder-patch`.
- **Root-cause hypothesis** generated with >85% confidence pointing to transcoder memory leak.
- **Business Impact Agent** computes ~1.8M affected viewers, ad window exposure, and business impact score (88/100).
- **Safety Director** evaluates `TRAFFIC_SHIFT` action against policy.

### Step 4: Remediation & Independent Verification
- **Remediation Agent** executes regional traffic shift to healthy standby cluster `transcoder-us-01`.
- **Verification Agent** independently queries post-remediation telemetry for 15 seconds.
- Telemetry error rate drops back to **0.4%**.
- Incident transitions to `RESOLVED`.
- Historical fingerprint saved and post-incident reports generated.

---

## 5. Automated Test Suite

Run full backend test suite:
```bash
cd backend
pytest tests/ -v
```

Run happy-path end-to-end integration test:
```bash
pytest tests/integration/test_e2e_workflow.py -v
```
