# Implementation Plan: Predictive Prevention & Proactive Remediation

**Branch**: `002-predictive-prevention` | **Date**: 2026-09-07 | **Spec**: [`specs/002-predictive-prevention/spec.md`](file:///c:/Coding_learning/studio_guardian/studio_guardian/specs/002-predictive-prevention/spec.md)

**Input**: Feature specification from [`specs/002-predictive-prevention/spec.md`](file:///c:/Coding_learning/studio_guardian/studio_guardian/specs/002-predictive-prevention/spec.md)

---

## Summary

Extend Studio Guardian from a purely reactive incident response system into a dual-mode **Predict → Prevent → Prove** platform. The system continuously ingests leading operational telemetry signals (GPU utilization, queue depth, transcode latency, error rate acceleration, concurrency growth) via **Grafana MCP**, calculates a deterministic, weighted predictive risk score ($0.0 - 1.0$), and engages a dedicated **Predictive Risk Agent** under the hierarchical supervision of the **Incident Commander**. 

The **Business Impact Agent** calculates counterfactual prevention economics (projected loss without action vs. cost of prevention), and the **Safety Director** enforces deterministic governance (risk $\ge 0.80$, confidence $\ge 0.85$, blast radius $\le 20\%$, and allowlist membership triggers `AUTO PREVENT`; otherwise gates to `WAITING_HUMAN_APPROVAL`). Following controlled preventive capacity scaling, the **Verification Agent** independently queries fresh telemetry to confirm that risk has collapsed below 25, displaying verified avoided exposure in an interactive **Predictive Operations** Command Center with 3D stress-to-safety visualization.

---

## Technical Context

**Language/Version**: Python 3.11+ (FastAPI backend), TypeScript 5.0+ (React frontend)

**Primary Dependencies**: 
- Backend: `fastapi`, `sqlalchemy` (v2.0 async), `pydantic` (v2), `google-genai` (Vertex AI SDK), `httpx` (async JSON-RPC MCP client), `uvicorn`
- Frontend: `react` (v18), `three` & `@react-three/fiber` / `@react-three/drei`, `lucide-react`, `tailwindcss`

**Storage**: PostgreSQL 16 (production) with automatic SQLite async (`sqlite+aiosqlite`) fallback for local development.

**Testing**: `pytest`, `pytest-asyncio` for unit, safety policy, and predictive engine tests.

**Target Platform**: Local Windows/macOS/Linux development environment and Google Cloud Run / Vertex AI Agent Engine.

**Project Type**: Autonomous Web Service + Real-Time 3D Broadcast Command Center.

**Performance Goals**:
- Deterministic risk model computation: $<50\text{ms}$
- Mode toggle switch (Predictive ↔ Reactive): $<500\text{ms}$
- End-to-end autonomous prevention cycle: $<90\text{s}$ from risk detection to verified resolution
- Reactive fallback escalation latency: $<3\text{s}$ upon critical threshold breach

**Constraints**:
- Purely deterministic risk calculations and confidence scoring in Python; zero hallucinated numerical values from LLMs.
- Gemini is strictly restricted to qualitative evidence synthesis, failure mode classification, and non-technical explanations (no chain-of-thought exposed).
- Strict allowlist for infrastructure mutations (`scale_transcoder_pool`, etc.).

**Scale/Scope**: 5–15 minute prediction horizon; 6 specialized agents; 6 new relational tables; 1 marquee live media streaming scenario (10.8M+ simulated viewers).

---

## Constitution Check

*GATE: Verified against [Studio Guardian Constitution](file:///c:/Coding_learning/studio_guardian/studio_guardian/.specify/memory/constitution.md). All 20 principles satisfied.*

| Principle | Assessment | Compliance Proof |
| :--- | :---: | :--- |
| **1. Real Agentic System** | PASS | Dedicated `PredictiveRiskAgent` added under the `IncidentCommander` supervisor; no monolithic prompt hacks. |
| **2. Hierarchical Supervisor** | PASS | Incident Commander delegates to Predictive Risk Agent, Business Impact Agent, Safety Director, Remediation Agent, and Verification Agent. |
| **3. Gemini is Reasoning Component** | PASS | Gemini interprets telemetry evidence and generates failure hypotheses; risk scoring and financials remain strictly in Python. |
| **4. Google Cloud Real Runtime** | PASS | Operates through `GoogleGenAIClient` with Vertex AI regional runtime, passing structured execution frames and run IDs to the UI. |
| **5. Grafana First-Class Integration** | PASS | Real Grafana MCP integration prioritized across Prometheus metrics, Loki logs, and alert evaluations. |
| **6. Media & Entertainment First** | PASS | Deep domain focus on transcode queues, rendition errors, segment fetch latency, GPU saturation, and viewer churn. |
| **7. Closed-Loop Autonomy** | PASS | Complete predictive lifecycle: Observe → Predict → Assess → Decide → Govern → Act → Verify → Prevented. |
| **8. Actual Remediation** | PASS | Remediation Agent executes controlled capacity scaling (`scale_transcoder_pool`) modifying the active simulator state. |
| **9. Independent Verification** | PASS | Verification Agent independently re-queries Grafana MCP post-action; requires $\ge 25\%$ GPU drop and risk $< 25$ before marking resolved. |
| **10. Safety By Design** | PASS | Deterministic Safety Director gates all mutations: risk $\ge 0.80$, confidence $\ge 0.85$, blast radius $\le 20\%$, allowlisted action. |
| **11. Persistent System of Record** | PASS | 6 new relational tables capture snapshots, evidence queries, decisions, actions, verifications, and memory fingerprints. |
| **12. Explainability Without CoT** | PASS | Plain-language, evidence-backed explanations presented in UI; internal model chain-of-thought tokens strictly withheld. |
| **15. Functionality Over Complexity** | PASS | Pure Python mathematical feature normalizer; no external ML training clusters, Kafka, or Kubernetes required. |
| **16. Demo-First Engineering** | PASS | Deterministic 4-step scenario (Healthy → Elevated → Imminent Auto-Prevent → Verified) designed for instant hackathon reproduction. |
| **20. Winner-Level Product** | PASS | Establishes Studio Guardian as an autonomous, proactive Incident Director purpose-built for high-stakes broadcast operations. |

---

## Project Structure

### Documentation (this feature)

```text
specs/002-predictive-prevention/
├── plan.md              # This file
├── research.md          # Phase 0 Research decisions
├── data-model.md        # Phase 1 Relational schemas & state machine
├── quickstart.md        # Phase 1 Runnable verification walkthrough
├── contracts/
│   ├── prediction-api.md # REST API endpoint specifications
│   └── sse-events.md     # Server-Sent Events schemas
└── tasks.md             # Phase 2 output (generated by /speckit-tasks)
```

### Source Code Layout

```text
backend/
├── src/
│   ├── agents/
│   │   ├── base.py
│   │   ├── incident_commander.py        # [MODIFY] Add predictive mode delegation & context inheritance
│   │   ├── predictive_risk_agent.py     # [NEW] Specialist agent querying MCP & orchestrating prediction
│   │   ├── business_impact_agent.py     # [MODIFY] Add prevention economics (loss vs. cost)
│   │   ├── remediation_agent.py         # [MODIFY] Add allowlisted preventive actions
│   │   └── verification_agent.py        # [MODIFY] Add before/after verification delta calculations
│   ├── prediction/
│   │   ├── __init__.py                  # [NEW] Module export
│   │   ├── feature_normalizer.py        # [NEW] SLO min-max clamping & 60s sliding regression slope
│   │   ├── risk_model.py                # [NEW] Deterministic weighted scoring & contributor breakdown
│   │   ├── predictor.py                 # [NEW] Time-to-threshold window & confidence engine
│   │   └── thresholds.py                # [NEW] Configurable weights, SLO floors/ceilings, tier bounds
│   ├── api/
│   │   ├── prediction.py                # [NEW] REST endpoints for status, evaluate, authorize, demo
│   │   └── stream.py                    # [MODIFY] Emit predictive SSE events
│   ├── persistence/
│   │   ├── models.py                    # [MODIFY] Define 6 new relational predictive entities
│   │   └── predictive_repository.py     # [NEW] CRUD operations for snapshots, decisions, verifications
│   ├── simulator/
│   │   └── media_env.py                 # [MODIFY] Add load-surge simulation & transcoder capacity scaling
│   └── main.py                          # [MODIFY] Mount prediction router
└── tests/
    └── unit/
        ├── test_predictive_engine.py    # [NEW] Test normalizer, risk model, and predictor
        └── test_predictive_safety.py    # [NEW] Test autonomous vs. gated safety decisions & verification

frontend/
├── src/
│   ├── types/
│   │   └── prediction.ts                # [NEW] TypeScript definitions for predictive state & events
│   ├── services/
│   │   └── predictionApi.ts             # [NEW] API client for prediction endpoints
│   ├── components/
│   │   ├── command-center/
│   │   │   ├── Header.tsx               # [MODIFY] Add Predictive ↔ Reactive Mode Switcher
│   │   │   ├── PredictiveDashboard.tsx  # [NEW] Primary Predictive Operations view
│   │   │   ├── UnifiedRuntimeLedger.tsx # [NEW] Chronological Vertex AI & Grafana MCP tool trace card
│   │   │   ├── RiskTrajectoryCard.tsx   # [NEW] Gauge and animated risk trend
│   │   │   ├── PreventionEconomicsCard.tsx # [NEW] Avoided exposure vs. scale cost trade-off
│   │   │   └── SafetyModal.tsx          # [MODIFY] Support preventive action authorization
│   │   └── canvas3d/
│   │       ├── BroadcastCore.tsx        # [MODIFY] Dynamic risk pulse lighting
│   │       └── ServiceNodes.tsx         # [MODIFY] Transcoder node stress shaders & capacity expansion
│   └── App.tsx                          # [MODIFY] Route between Predictive and Reactive dashboard views
```

---

## Complexity Tracking

> **No Constitution Violations**. Pure Python deterministic mathematical models are utilized, strictly avoiding custom ML infrastructure, external model training pipelines, or unneeded microservices.
