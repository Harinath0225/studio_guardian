# Studio Guardian 🛡️
### Autonomous Live Media Incident Director
*Built for the Google Cloud & Grafana Labs Hackathon*

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://react.dev/)
[![Three.js](https://img.shields.io/badge/Three.js-R3F-purple.svg)](https://docs.pmnd.rs/react-three-fiber)
[![Gemini](https://img.shields.io/badge/Gemini_2.5-Google_Cloud-orange.svg)](https://cloud.google.com/vertex-ai)
[![Grafana](https://img.shields.io/badge/Grafana-MCP-F46800.svg)](https://grafana.com/)

---

## 📺 Overview

During major live entertainment streaming events (e.g. World Cup finals, Super Bowl, live stadium concerts), infrastructure degradation causes instant playback buffering, advertiser revenue burn, and subscriber churn.

**Studio Guardian** is an autonomous multi-agent incident director that manages the full streaming incident lifecycle:
1. **Detects** stream degradation via Grafana Alerting.
2. **Investigates** operational telemetry across **Prometheus**, **Loki**, and **Tempo** via **Grafana MCP**.
3. **Diagnoses** root-cause hypotheses with **Gemini 2.5 on Google Cloud**.
4. **Quantifies** commercial audience disruption and ad revenue at risk.
5. **Governs** remediation through a deterministic **Safety Director** (25% blast radius cap).
6. **Remediates** by dynamically shifting video proxy routing to warm-standby clusters.
7. **Independently Verifies** telemetry stabilization before marking incidents resolved.
8. **Generates** automated post-incident Engineering RCAs and Executive Briefs.

---

## 🚀 Key Innovations

- **Authentic Multi-Agent System**:
  - `Incident Commander`: Supervisory state machine with retry loops and human escalation gating.
  - `Observability Investigator`: Multi-signal correlation agent powered by Grafana MCP tool calls.
  - `Business Impact Agent`: Mathematical audience blast and ad revenue calculation.
  - `Safety Director`: Deterministic policy engine enforcing strict action allowlists and blast radius ceilings.
  - `Remediation Agent`: Controlled traffic shifting against video routing proxies.
  - `Verification Agent`: Impartial post-action telemetry validator.
- **Grafana Model Context Protocol (MCP)**:
  - Real MCP tools: `query_prometheus_metrics`, `search_loki_logs`, `get_tempo_traces`, `list_grafana_alerts`.
  - Transparent high-fidelity local mock provider for reliable offline demonstration.
- **Google Cloud & Gemini 2.5**:
  - Integrated via official `google-genai` SDK and Vertex AI with Pydantic v2 structured schemas.
- **Cinematic Command Center**:
  - React 18, TypeScript, TailwindCSS, and React Three Fiber 3D spatial broadcast mesh globe.
  - Real-time 1 Hz telemetry streaming via Server-Sent Events (SSE).

---

## ⚡ Quickstart (Local Development)

### 1. Prerequisites
- Python 3.12+ and `uv`
- Node.js 18+ and `npm`

### 2. Backend Setup
```bash
cd backend
python -m venv .venv

# Activate virtualenv:
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

uv pip install -r pyproject.toml
uvicorn src.main:app --port 8000 --reload
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open **http://localhost:5173** to view the live Command Center.

---

## 🎯 3-Minute Automated Demo Runner

To run the automated end-to-end judge reproduction script:
```bash
python scripts/run_demo.py
```

---

## 🧪 Comprehensive Testing Suite

Execute the automated test suite (41 tests passing):
```bash
cd backend
pytest -v
```

---

## 📂 Documentation

- **[ARCHITECTURE.md](file:///c:/Coding_learning/studio_guardian/studio_guardian/ARCHITECTURE.md)**: System topology, Mermaid diagrams, and agent boundaries.
- **[DEMO.md](file:///c:/Coding_learning/studio_guardian/studio_guardian/DEMO.md)**: Step-by-step judge reproduction instructions.
- **[SECURITY.md](file:///c:/Coding_learning/studio_guardian/studio_guardian/SECURITY.md)**: Deterministic safety policy and governance rules.
- **[docs/DEPLOYMENT.md](file:///c:/Coding_learning/studio_guardian/studio_guardian/docs/DEPLOYMENT.md)**: Google Cloud Run and Cloud SQL deployment guide.
- **[docs/SUBMISSION.md](file:///c:/Coding_learning/studio_guardian/studio_guardian/docs/SUBMISSION.md)**: Hackathon submission summary and video script outline.

---

## 📜 License

Studio Guardian is open source licensed under the **[Apache 2.0 License](file:///c:/Coding_learning/studio_guardian/studio_guardian/LICENSE)**.
