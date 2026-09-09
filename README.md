# Studio Guardian 🛡️
### Autonomous Live Media Incident Director & Predictive Defense System
*Built for the Google Cloud & Grafana Labs Hackathon*

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://react.dev/)
[![Three.js](https://img.shields.io/badge/Three.js-R3F-purple.svg)](https://docs.pmnd.rs/react-three-fiber)
[![Gemini](https://img.shields.io/badge/Gemini_3.6_Flash-Google_Cloud-orange.svg)](https://cloud.google.com/vertex-ai)
[![Grafana](https://img.shields.io/badge/Grafana-MCP-F46800.svg)](https://grafana.com/)

---

## 📺 Overview

During massive live broadcast events (e.g. World Cup finals, Super Bowl, live stadium concerts), infrastructure stalls or ad cue corruptions cause instant viewer rebuffering, sponsor SLA penalties, and brand damage.

**Studio Guardian** is an autonomous dual-track incident director and predictive defense system:
1. **Predicts & Prevents**: Continuously sweeps leading signals across **GPU compute**, **worker queues**, **segment latencies**, and **SCTE-35 ad cues** to mitigate capacity saturation 5–15 minutes before customer playback degrades.
2. **Triages & Responds**: If acute degradation strikes, transitions seamlessly to emergency triage (<500ms) with multi-signal correlation across **Prometheus**, **Loki**, and **Tempo** via **Grafana MCP**.
3. **Semantic Media Quality**: Specialized media sentinels detect **SCTE-35 ad splice drift** and **EBU R128 loudness / lip-sync drift** even when CPU and GPU metrics appear nominal.
4. **Deterministic Governance**: A strict **Safety Director** enforces a 20% blast radius ceiling and confidence thresholds before dispatching capacity scaling or traffic shifting.
5. **Live Observability & Streaming**: Built-in 1 Hz streaming console with real-time **Prometheus metrics** and **Loki log streaming**, plus 1-click integration with **Grafana Cloud**.

---

## 🚀 Key Innovations & Architecture

### 1. Dual-Track Multi-Agent System
- **`Incident Commander`**: Supervisory hierarchical state machine managing proactive prevention and reactive emergency triage.
- **`Predictive Risk Agent`**: Computes weighted risk projections ($R(t) = \sum w_i \cdot s_i(t)$) and time-to-impact windows.
- **`SCTE-35 Ad Integrity Sentinel`**: Monitors ad cue timing drift (±200ms bounds), splice alignment mismatch, and ad pod drop rates.
- **`Perceptual Quality Sentinel`**: Audits EBU R128 audio loudness (-24 LUFS), A/V lip-sync drift, and video frame drop ratios.
- **`Observability Investigator`**: Multi-signal root cause correlation via real **Grafana MCP** tool calls.
- **`Business Impact Agent`**: Mathematical calculation of audience blast radius, ad revenue burn, and counterfactual avoided loss.
- **`Safety Director`**: Deterministic gating enforcing strict action allowlists, blast radius limits, and human approval gates.
- **`Remediation Agent`**: Executes minimal-blast mitigations (`scale_transcoder_pool`, `traffic_shift`).
- **`Verification Agent`**: Impartial post-action validator calculating independent telemetry deltas ($\Delta\text{GPU} \le -25\%$).

### 2. Five Operational Views in Cinematic Command Center
1. **`1. PREDICT`**: Predictive horizon, real-time risk trajectory, contributing signal breakdown, and mathematical provenance drawer.
2. **`2. PROTECT`**: Policy engine audit, autonomous pool scaling vs human approval modal, and blast radius guardrails.
3. **`3. RESPOND`**: Reactive incident fallback, standby cluster routing, and agent timeline ledger.
4. **`4. GAME DAY`**: Deterministic Black Swan chaos engine (`TRANSCODER_SURGE`, `SCTE35_CORRUPTION`, `BASELINE_RESET`).
5. **`5. GRAFANA LIVE`**: Native In-Website Observability Console featuring:
   - **Live Prometheus Streaming Charts** (GPU saturation, segment latency vs 500ms SLA, SCTE-35 drift, buffer errors).
   - **Live Loki Terminal Log Stream** with syntax highlighting, search filter, severity level filter, auto-scroll, and pause/resume.
   - **Grafana Cloud Bridge** with direct dashboard link, 1-click JSON export, and Loki ingestion diagnostics.

### 3. Grafana Model Context Protocol (MCP) & Cloud Integration
- Real MCP tools: `query_prometheus`, `query_loki_logs`, `tempo_get-trace`, `alerting_manage_rules`.
- Standard Prometheus exposition scrape endpoint at `/metrics`.
- Real-time Server-Sent Events (SSE) telemetry and log stream at `/api/v1/stream/events`.
- Direct Grafana Cloud Loki log shipper with Cloud Access Policy authentication.
- Pre-built, 1-click importable Grafana Cloud dashboard: [`grafana/studio-guardian-dashboard.json`](file:///c:/Coding_learning/studio_guardian/studio_guardian/grafana/studio-guardian-dashboard.json).

---

## ⚡ Quickstart

### 1. Prerequisites
- Python 3.12+ (or `uv`)
- Node.js 18+ and `npm`
- Docker (optional, for local Postgres and official Grafana MCP container)

### 2. Environment Configuration
Create or edit `.env` in the root directory:
```env
# Server
PORT=8000
HOST=0.0.0.0

# Database
DATABASE_URL=sqlite+aiosqlite:///./studio_guardian.db
DATABASE_URL_SYNC=sqlite:///./studio_guardian.db

# Google Cloud / Gemini
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_GENAI_USE_VERTEXAI=true
GEMINI_MODEL=gemini-3.6-flash

# Grafana MCP & Cloud Integration
GRAFANA_URL=https://whitepenguin2589.grafana.net
GRAFANA_SERVICE_ACCOUNT_TOKEN=glsa_your_service_account_token
GRAFANA_LOKI_TOKEN=glc_your_cloud_access_policy_token
USE_MOCK_GRAFANA_MCP=true
```

### 3. Backend Setup
```bash
# Using uv (recommended):
uv run --with-requirements backend/requirements.txt uvicorn src.main:app --port 8000 --reload

# Or standard virtualenv:
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --port 8000 --reload
```

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open **[http://localhost:5173](http://localhost:5173)** in your browser.

---

## 🎯 Game Day Chaos Testing

You can trigger deterministic Black Swan chaos and observe real-time agent mitigations:

1. Open **[http://localhost:5173](http://localhost:5173)**.
2. Navigate to **`4. GAME DAY (Black Swan Chaos)`**.
3. Choose a scenario:
   - **`Transcoder Surge`**: Simulates a 4K/HDR concurrency surge. Leading indicators escalate (GPU >90%, worker queue >40 chunks) while playback error stays nominal. Proves leading indicator detection.
   - **`SCTE-35 Corruption`**: Simulates cue timing drift (+420ms) and splice mismatch. Infrastructure stays green while media quality degrades. Proves semantic media observability.
   - **`Baseline Reset`**: Restores nominal healthy streaming baseline.
4. Switch to **`5. GRAFANA LIVE`** to watch the Prometheus charts spike and Loki logs stream in real time.
5. Switch to **`1. PREDICT`** and **`2. PROTECT`** to observe autonomous capacity scaling and mathematical provenance.

---

## ☁️ Grafana Cloud Setup

If you want to view dashboards directly inside your hosted Grafana Cloud instance (`whitepenguin2589.grafana.net`):

1. **Import the Pre-Configured Dashboard**:
   - In Studio Guardian, click **`5. GRAFANA LIVE`** &rarr; **`3. Grafana Cloud Setup & Embed`** &rarr; **`Copy JSON`**.
   - In Grafana Cloud, click **`New`** &rarr; **`Import`** &rarr; paste the JSON &rarr; click **`Import`**.
   - *Or open your live published dashboard directly:* [https://whitepenguin2589.grafana.net/d/ah2f7v/192737d](https://whitepenguin2589.grafana.net/d/ah2f7v/192737d).
2. **Ship Logs to Grafana Cloud Loki**:
   - In [grafana.com/orgs](https://grafana.com/orgs), create an **Access Policy** with `logs:write` scope.
   - Set `GRAFANA_LOKI_TOKEN=glc_...` in `.env`.
   - Studio Guardian will automatically ship structured logs to `https://logs-prod-026.grafana.net/loki/api/v1/push`.
3. For detailed step-by-step instructions, see [docs/GRAFANA_CLOUD_SETUP_GUIDE.md](file:///c:/Coding_learning/studio_guardian/studio_guardian/docs/GRAFANA_CLOUD_SETUP_GUIDE.md).

---

## 🧪 Verification & Testing

Execute the automated test suite covering unit tests, Grafana MCP integration, and observability:
```bash
uv run --with-requirements backend/requirements.txt pytest backend/tests/integration/test_grafana_mcp.py backend/tests/unit/test_observability.py
```

Build the production frontend bundle:
```bash
npm --prefix frontend run build
```

---

## 📂 Documentation Directory

- **[ARCHITECTURE.md](file:///c:/Coding_learning/studio_guardian/studio_guardian/ARCHITECTURE.md)**: System topology, agent contracts, state machine, and data flow.
- **[docs/GRAFANA_CLOUD_SETUP_GUIDE.md](file:///c:/Coding_learning/studio_guardian/studio_guardian/docs/GRAFANA_CLOUD_SETUP_GUIDE.md)**: Comprehensive Grafana Cloud and token configuration guide.
- **[docs/MATHEMATICAL_PROVENANCE.md](file:///c:/Coding_learning/studio_guardian/studio_guardian/docs/MATHEMATICAL_PROVENANCE.md)**: Mathematical risk formula, normalization weights, and verifiable hashing.
- **[docs/VERTEX_AI_RUNTIME.md](file:///c:/Coding_learning/studio_guardian/studio_guardian/docs/VERTEX_AI_RUNTIME.md)**: Google Cloud Vertex AI and Gemini runtime integration.
- **[DEMO.md](file:///c:/Coding_learning/studio_guardian/studio_guardian/DEMO.md)**: 3-minute hackathon judge evaluation walkthrough.
- **[SECURITY.md](file:///c:/Coding_learning/studio_guardian/studio_guardian/SECURITY.md)**: Deterministic safety policy and governance rules.

---

## 📜 License

Studio Guardian is open source licensed under the **[Apache 2.0 License](file:///c:/Coding_learning/studio_guardian/studio_guardian/LICENSE)**.
