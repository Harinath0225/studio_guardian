# Implementation Plan: Predictive Media Protection & Black Swan Defense

**Branch**: `003-predictive-defense` | **Date**: 2026-09-08 | **Spec**: [specs/003-predictive-defense/spec.md](file:///c:/Coding_learning/studio_guardian/studio_guardian/specs/003-predictive-defense/spec.md)

**Input**: Feature specification from `/specs/003-predictive-defense/spec.md`

---

## Summary

Extend the Studio Guardian modular monolith with an autonomous, dual-lifecycle media reliability system:
1. **Predictive Media Protection (Predict → Prevent → Prove)**: Ingests live telemetry via Grafana MCP, applies deterministic feature normalization and 60s sliding regression trend analysis, computes composite risk and failure horizon window, governs actions through a deterministic Safety Director policy engine, executes controlled Transcoder Capacity Scaling (`scale_transcoder_pool`), and independently verifies risk mitigation with fresh Grafana MCP data.
2. **Black Swan Defense (Detect → Investigate → Remediate → Verify)**: Provides deterministic chaos injection for Transcoder Capacity Surge and SCTE-35 Corruption, triggering multi-agent investigation, traffic shifting or slate fallback, and verification.
3. **Architectural Grounding**: Orchestrated by a root Incident Commander via Google Cloud Vertex AI Agent Engine with transparent mathematical provenance and a lightweight React Three Fiber 3D operational graph.

---

## Technical Context

- **Language/Version**: Python 3.11+ (Backend), TypeScript 5.4+ (Frontend)
- **Primary Dependencies**:
  - *Backend*: FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), `google-genai` SDK (`vertexai=True`), `mcp` SDK, `httpx`, `pytest`, `pytest-asyncio`
  - *Frontend*: React 18, Vite, `@react-three/fiber` 8.x, `@react-three/drei` 9.x, `three` 0.165, `recharts`, `lucide-react`, Tailwind CSS
- **Storage**: SQLite (local development with `aiosqlite`) / PostgreSQL (Cloud SQL in GCP), Alembic migrations
- **Testing**: `pytest` (Unit, Integration, E2E), Vitest / React Testing Library
- **Target Platform**: Local development on Windows/macOS/Linux; Production deployment on Google Cloud Run + Vertex AI Agent Engine + Cloud SQL
- **Project Type**: Web Application (FastAPI Modular Monolith Backend + React SPA Frontend)
- **Performance Goals**: Telemetry ingestion & normalization <200ms p95; Risk model calculation <50ms; 3D topology rendering 60 fps
- **Constraints**: Strict out-of-scope enforcement (no custom ML training, no Kubernetes, no Kafka, no vector DBs, no broadcast-grade QC hardware)
- **Scale/Scope**: Live broadcast simulation handling 12.4M concurrent viewers across 4 regional clusters (AU, SG, IN, US)

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Compliance Status | Justification / Implementation Reference |
|---|---|---|---|
| **1. Vertex AI Agent Runtime** | Vertex AI is the actual runtime, exposing agent identity, session ID, execution frames | **PASS** | Incident Commander and Specialist Agents execute via `google-genai` with `vertexai=True`, maintaining session frames and exposed in UI |
| **2. Gemini Reasoning Layer** | Gemini interprets evidence, does NOT invent telemetry or calculate math | **PASS** | All numerical risk scores, normalization, and financial loss calculations are strictly deterministic in Python; Gemini only synthesizes hypotheses |
| **3. Grafana MCP Source of Truth** | All telemetry queries execute over Grafana MCP `streamable-http` transport | **PASS** | `GrafanaMCPClient` queries Prometheus, Loki, Tempo at `http://localhost:8001/mcp` with `Mcp-Session-Id`; responses persisted in `runtime_evidence` |
| **4. Mathematically Traceable Data** | Raw value → Normalization → Formula → Result → Provenance | **PASS** | Every intermediate calculation is persisted in `risk_contributions` and exposed via `/api/v1/predictive/provenance` |
| **5. Predict Before Failure** | Monitor → Detect → Calculate → Predict → Assess → Govern → Prevent → Verify | **PASS** | Flagship predictive lifecycle implemented across `predictive_risk_agent.py`, `risk_model.py`, and `thresholds.py` |
| **6. Reactive Fallback** | Prediction must cleanly fall back to incident response if failure occurs | **PASS** | Existing Incident Commander reactive investigation and traffic shifting workflow maintained as fallback |
| **7. Media Domain Intelligence** | Live streaming, SCTE-35, AV sync, transcoding, ad pods, SLA liability | **PASS** | Domain-specific simulator and evaluation engines built for real broadcast signals |
| **8. Semantic Media Quality** | Detect degradation when CPU/Memory appear healthy | **PASS** | SCTE-35 drift and perceptual quality anomalies evaluated independently of infrastructure CPU/Memory |
| **9. Ad Integrity Business Critical** | Configured operational tolerance used; no unsupported standards claims | **PASS** | Explicit configured operational tolerance (±200ms) with no unsupported compliance claims |
| **10. Perceptual Quality Limited** | Lightweight signal only: AV sync, loudness, dropped frames, black frames | **PASS** | Strictly bounded to 4 measurable scalars; no professional QC platform emulation |
| **11. Safety Before Autonomy** | Deterministic policy governs automated remediation | **PASS** | Safety Director enforces Risk ≥0.80, Confidence ≥0.85, Blast Radius ≤20%, and allowlisted actions |
| **12. Calculable Business Value** | Transparent formulas for viewer loss, ad burn, SLA penalty, net avoided loss | **PASS** | Deterministic formulas in `impact_model.py` with formula versioning |
| **13. Black Swan Game Day** | Deterministic chaos injection facility without code changes | **PASS** | UI chaos buttons for `TRANSCODER_SURGE` and `SCTE35_CORRUPTION` in `scenarios.py` |
| **14. Counterfactual Honesty** | Financial output labeled as "Estimated Exposure Avoided", not observed savings | **PASS** | Strict provenance labeling (`ESTIMATED` vs `OBSERVED`) across all outputs |
| **15. Closed-Loop Proof** | Grafana evidence → Math → Agent → Policy → Action → Fresh Grafana evidence → Verify | **PASS** | Independent verification compares BEFORE vs AFTER telemetry from Grafana MCP post-stabilization |
| **16. UX: Broadcast Ops Center** | Modern, premium, cinematic UI with non-gimmick 3D topology | **PASS** | 4 operational views (PREDICT, PROTECT, RESPOND, GAME DAY) and React Three Fiber system graph |
| **17. Demo-First Priority** | Flagship Predict → Prevent → Verify and Black Swan scenarios | **PASS** | Reproducible demonstration runnable in <90 seconds |
| **18. Hackathon Compliance** | Public open-source readiness, real GCP runtime, real Grafana MCP | **PASS** | Full compliance with GCP, Vertex AI, and Grafana hackathon requirements |

---

## Project Structure

### Documentation (this feature)

```text
specs/003-predictive-defense/
├── spec.md              # Feature specification with clarifications
├── plan.md              # This technical implementation plan
├── research.md          # Phase 0 architectural decisions & rationales
├── data-model.md        # Phase 1 database entities, relationships & transitions
├── quickstart.md        # Phase 1 runnable validation guide
├── contracts/           # Phase 1 HTTP API contracts
│   └── api-contracts.md
└── checklists/
    └── requirements.md  # Quality checklist (16/16 passing)
```

### Source Code Architecture (Modular Monolith)

```text
backend/
├── src/
│   ├── main.py                     # FastAPI application entry point & CORS
│   ├── config.py                   # Pydantic BaseSettings & environment config
│   ├── agents/                     # Vertex AI Specialist & Commander Agents
│   │   ├── base.py                 # BaseAgent with Vertex AI session trace frames
│   │   ├── incident_commander.py   # Root Incident Commander orchestrator
│   │   ├── predictive_risk_agent.py# Predictive Risk specialist
│   │   ├── investigator.py         # Observability Investigator
│   │   ├── impact.py               # Business Impact Agent
│   │   ├── remediation.py          # Remediation Agent
│   │   └── verifier.py             # Verification Agent
│   ├── prediction/                 # Deterministic Predictive Engine
│   │   ├── normalizer.py           # SLO min-max feature normalization [0.0, 1.0]
│   │   ├── features.py             # Derived feature transformers
│   │   ├── trend.py                # 60s sliding regression slope & acceleration
│   │   ├── thresholds.py           # Operational risk tiers & triggers
│   │   ├── risk_model.py           # Weighted composite risk & saturation booster
│   │   ├── predictor.py            # Time-to-threshold & confidence estimator
│   │   └── provenance.py           # Mathematical lineage metadata builder
│   ├── media/                      # Semantic Media & Ad Specialists
│   │   ├── ad_integrity.py         # SCTE-35 cue drift & splice alignment evaluator
│   │   └── perceptual_quality.py   # AV sync, loudness, frame-drop calculator
│   ├── business/                   # Commercial & Counterfactual ROI Engine
│   │   └── impact_model.py         # Viewer, ad revenue, SLA & prevention economics
│   ├── policy/                     # Deterministic Governance
│   │   └── safety_director.py      # Blast radius & confidence policy gatekeeper
│   ├── simulator/                  # Broadcast Media Simulator & Chaos
│   │   ├── media_env.py            # Streaming cluster state & capacity pool
│   │   ├── metrics_generator.py    # Multi-dimensional telemetry generator
│   │   ├── video_proxy.py          # Controlled traffic shifting & routing proxy
│   │   └── injector.py             # Failure injector adapter
│   ├── demo/                       # Black Swan Gameday Scenarios
│   │   └── scenarios.py            # TRANSCODER_SURGE & SCTE35_CORRUPTION scenarios
│   ├── integrations/               # External System Adapters
│   │   ├── google_genai.py         # Vertex AI Agent Engine client
│   │   ├── mcp_client.py           # Grafana MCP streamable-http client
│   │   ├── mcp_tools.py            # Typed tool wrappers for Grafana MCP
│   │   └── mock_grafana.py         # Local offline deterministic Grafana mock
│   ├── persistence/                # Storage & Repositories
│   │   ├── database.py             # SQLAlchemy async engine & sessionmaker
│   │   ├── models.py               # Declarative ORM models
│   │   ├── predictive_repository.py# Data access for snapshots, actions & evidence
│   │   └── repository.py           # Data access for incidents & agent runs
│   └── api/                        # HTTP Routers
│       ├── predictive.py           # /api/v1/predictive endpoints
│       ├── media.py                # /api/v1/media endpoints
│       ├── demo.py                 # /api/v1/demo/black-swan endpoints
│       └── evidence.py             # /api/v1/evidence endpoints
└── tests/
    ├── unit/                       # Risk model, normalization, policy & media math tests
    ├── integration/                # Grafana MCP adapter & Vertex AI client tests
    └── e2e/                        # Predict->Prevent->Verify & Black Swan workflows

frontend/
├── src/
│   ├── App.tsx                     # Main layout & view navigation
│   ├── components/
│   │   ├── command-center/
│   │   │   ├── PredictView.tsx     # PREDICT: risk gauge, trend, failure window, contributors
│   │   │   ├── ProtectView.tsx     # PROTECT: actions, economics, policy verdict
│   │   │   ├── RespondView.tsx     # RESPOND: incident investigation & recovery
│   │   │   ├── GameDayView.tsx     # GAME DAY: Black Swan scenario injection
│   │   │   ├── TechnicalEvidencePanel.tsx # Vertex AI -> Specialist -> Grafana MCP flow
│   │   │   └── DataProvenanceDrawer.tsx   # Mathematical lineage inspection drawer
│   │   ├── canvas3d/
│   │   │   └── SystemTopology3D.tsx# React Three Fiber broadcast system graph
│   │   └── common/                 # Badges, metrics cards, tooltips
│   ├── services/
│   │   ├── api.ts                  # REST API client
│   │   └── sse.ts                  # Live telemetry & event stream handler
│   └── types/
│       └── index.ts                # TypeScript interfaces for API contracts
```

---

## Detailed Implementation Breakdown

### 1. Root Incident Commander & Vertex AI Agent Runtime
- **Component**: `backend/src/agents/incident_commander.py` & `google_genai.py`
- Root orchestrator running under Google Vertex AI Agent Engine (`google-genai` with `vertexai=True`).
- Dispatches tasks to specialist sub-agents based on operational stage:
  - In normal/pre-incident state: dispatches to `PredictiveRiskAgent`, `AdIntegrityAgent`, `PerceptualQualitySentinel`.
  - In degradation state: dispatches to `Investigator`, `BusinessImpactAgent`, `RemediationAgent`, `Verifier`.
- Exposes runtime session identifier, agent state, current specialist, and execution trace frames.

### 2. Grafana MCP Adapter & Evidence Persistence
- **Component**: `backend/src/integrations/mcp_client.py` & `persistence/models.py`
- Connects over `streamable-http` at `http://localhost:8001/mcp` with `Mcp-Session-Id`.
- Strictly enforces tool allowlists:
  - Predictive: `query_prometheus`, `query_loki_logs`.
  - Reactive: `query_prometheus`, `query_loki_logs`, `alerting_manage_rules`, `tempo_get-trace`.
  - Verification: Fresh telemetry queries.
- Persists all executions into `runtime_evidence` table (tool name, query metadata, raw response JSON, duration, agent).

### 3. Realistic Media Simulator & Telemetry Pipeline
- **Component**: `backend/src/simulator/media_env.py` & `metrics_generator.py`
- Generates multi-dimensional broadcast signals:
  - Transcoding: GPU utilization (50–98%), queue depth (5–140), latency (150–500ms).
  - Audience: 12.4M concurrent viewers across AU, SG, IN, US.
  - SCTE-35: Cue timing drift (0–500ms), splice alignment error, ad pod drop percentage.
  - Perceptual: AV sync offset (-50 to +250ms), loudness (-24 ± 4 LUFS), frame drop (0–10%), black frames (0–5%).
- Telemetry dynamically transitions upon scenario injection and recovers upon remediation.

### 4. Deterministic Predictive Engine
- **Component**: `backend/src/prediction/`
- `normalizer.py`: Clamps metrics into dimensionless `[0.0, 1.0]` using defined SLO boundaries.
- `trend.py`: Computes 60s sliding regression slope (`dy/dt`) and 2nd derivative acceleration (`d²y/dt²`).
- `risk_model.py`: Calculates weighted risk score `[0.0, 1.0]` with compound saturation booster (GPU >85% and queue >80% elevates priority).
- `predictor.py`: Bounds failure window between 3 and 15 minutes; calculates independent confidence `[0.0, 1.0]` (freshness 35%, completeness 35%, concordance 30%).
- `provenance.py`: Generates mathematical lineage records with exact formulas and coefficients.

### 5. Media Specialist Engines
- **Component**: `backend/src/media/`
- `ad_integrity.py`: Evaluates SCTE-35 cue timing against configured operational tolerance (±200ms).
- `perceptual_quality.py`: Evaluates AV sync drift, loudness deviation, dropped frames ratio, black frame ratio.
- Persists anomalies into `ad_integrity_events` and `media_quality_events`.

### 6. Business Impact & Counterfactual ROI
- **Component**: `backend/src/business/impact_model.py`
- Transparent formulas for disrupted viewers, ad revenue burn rate (CPM $28.50), SLA penalties.
- Proactive preventive savings calculated as: `expected_loss_without_action - expected_loss_after_action - cost_of_prevention`.
- Labeled explicitly as `ESTIMATED` with formula version metadata.

### 7. Safety Director Policy Engine
- **Component**: `backend/src/policy/safety_director.py`
- Deterministic rules:
  - If `risk >= 0.80` AND `confidence >= 0.85` AND `blast_radius <= 0.20` AND `action in ALLOWLIST` → `AUTO_EXECUTE`.
  - Else → `REQUIRES_HUMAN_APPROVAL`.
- Records policy decisions in `prevention_actions`.

### 8. Controlled Remediation Fabric & Verification Pipeline
- **Component**: `backend/src/agents/remediation.py` & `verifier.py`
- Allowlisted actions: `scale_transcoder_pool` (doubles worker nodes from 8 to 16), `shift_traffic`, `activate_ad_slate`, `switch_packager`.
- Post-action stabilization delay (5s simulation), followed by fresh Grafana MCP query.
- Compares BEFORE vs. AFTER values and marks outcome: `PREVENTION_VERIFIED` / `RECOVERED` or `FAILED`.

### 9. Black Swan Gameday Scenarios
- **Component**: `backend/src/demo/scenarios.py`
- `TRANSCODER_SURGE`: Triggers 4K/HDR load surge, escalating GPU to 93.4% and queue to 48.
- `SCTE35_CORRUPTION`: Triggers SCTE-35 cue timing drift (>350ms) and corrupt splice payloads.
- Reset endpoint restores nominal baseline telemetry.

### 10. Frontend: 4 Operational Views & 3D Graph
- **Component**: `frontend/src/components/command-center/` & `canvas3d/`
- **PREDICT View**: Real-time risk gauge, 60s trend graph, failure window countdown, signal contributor breakdown.
- **PROTECT View**: Candidate prevention card, economics comparison, Safety Director verdict badge, one-click execution.
- **RESPOND View**: Active incident diagnostics, root cause tree, remediation log, verification delta.
- **GAME DAY View**: Scenario selection cards, "Inject Black Swan" buttons, live event progression bar.
- **SystemTopology3D**: Three.js canvas showing ingest, transcoders, packagers, ADS, CDN, and regional nodes with stress animations and data particle flows.
- **Technical Evidence Panel**: Live execution breadcrumb showing `Vertex AI → Specialist → Grafana MCP → Raw Telemetry → Risk Model → Gemini`.
- **Data Provenance Drawer**: Slide-over modal displaying exact formulas, raw values, and mathematical derivation.

---

## Deployment Architecture

- **Application Backend**: Containerized FastAPI modular monolith deployed on **Google Cloud Run**.
- **Agent Runtime**: **Google Cloud Vertex AI Agent Engine** authenticated via Google Cloud Application Default Credentials (ADC) or Express API key.
- **System of Record**: **Google Cloud SQL for PostgreSQL** (or local SQLite for containerized gameday demo).
- **Observability**: **Grafana Cloud** (or local Docker Grafana MCP server) exposing Prometheus metrics, Loki logs, and Tempo traces.
- **Secrets Management**: **Google Cloud Secret Manager** storing `GRAFANA_SERVICE_ACCOUNT_TOKEN` and GCP credentials.
- **Frontend SPA**: Static build hosted via **Cloud Storage + Cloud CDN** or Vite dev server.

---

## Verification Plan

### Automated Tests
1. **Unit Tests** (`backend/tests/unit/`):
   - `test_normalizer.py`: Validate min-max clamping across all SLO bounds.
   - `test_trend.py`: Validate 60s sliding regression slope and acceleration calculations.
   - `test_risk_model.py`: Validate weighted composite scoring and compound saturation boosting.
   - `test_safety_director.py`: Validate deterministic policy gating (`AUTO_EXECUTE` vs. `REQUIRES_HUMAN_APPROVAL`).
   - `test_ad_integrity.py`: Validate SCTE-35 timing drift detection against operational tolerance.
   - `test_perceptual_quality.py`: Validate AV sync, loudness, and frame-drop formulas.
   - `test_business_impact.py`: Validate counterfactual ROI formulas and provenance labeling.
2. **Integration Tests** (`backend/tests/integration/`):
   - `test_mcp_client.py`: Validate streamable-http JSON-RPC 2.0 handshake and session ID handling.
   - `test_google_genai.py`: Validate Vertex AI Agent Engine structured output and offline fallback.
   - `test_predictive_repository.py`: Validate CRUD operations on snapshots, decisions, and evidence.
3. **End-to-End Tests** (`backend/tests/e2e/`):
   - `test_predictive_workflow.py`: End-to-end `PREDICT → PREVENT → PROVE` cycle with `scale_transcoder_pool`.
   - `test_black_swan_scenarios.py`: End-to-end `INJECT → DETECT → RESPOND → VERIFY` cycle for both scenarios.

### Manual Verification Scenarios
- **Scenario 1**: Launch UI, open **PREDICT** tab, click **"Inject Transcoder Surge"** in **GAME DAY**, observe risk spike to >0.85, verify failure window countdown (3–7 mins), click **"Execute Transcoder Scale"** in **PROTECT**, observe GPU drop to ~61%, and confirm "PREDICTED RISK MITIGATED" status.
- **Scenario 2**: Click **"Inject SCTE-35 Corruption"**, confirm Ad Integrity Sentinel triggers alert, inspect estimated ad exposure, execute secondary path switch, and verify nominal SCTE alignment.
- **Scenario 3**: Click any metric number to open the **Data Provenance Drawer** and verify that raw Grafana MCP queries, SLO bounds, and formulas display truthfully.
