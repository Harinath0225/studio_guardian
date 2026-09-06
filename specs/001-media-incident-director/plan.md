# Implementation Plan: Studio Guardian — Autonomous Live Media Incident Director

**Branch**: `001-media-incident-director` | **Date**: 2026-09-06 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-media-incident-director/spec.md`

## Summary

Studio Guardian is an autonomous multi-agent incident director for live media broadcasts. It detects live streaming degradation (e.g. "India vs Australia Final"), coordinates a hierarchical team of specialist agents using Google Cloud Agent Development Kit (ADK) and Gemini on Cloud Run, gathers operational evidence via a runtime Grafana MCP integration, determines blast-radius and policy with a deterministic Safety Director, executes safe traffic-shifting remediation against a live mock video routing proxy, independently verifies telemetry recovery, and visualizes the complete closed-loop lifecycle on a cinematic React / Three.js Command Center UI with Server-Sent Events (SSE).

## Technical Context

**Language/Version**: Python 3.12+ (Backend), TypeScript 5.4+ / Node.js 20+ (Frontend)

**Primary Dependencies**:
- **Backend**: FastAPI, Pydantic v2, Google GenAI SDK (`google-genai` / ADK), `mcp` Python SDK (Model Context Protocol client), SQLAlchemy 2.x, asyncpg, Alembic, uvicorn, sse-starlette.
- **Frontend**: React 18, Vite, TypeScript, TailwindCSS, React Three Fiber (`@react-three/fiber`), `@react-three/drei`, Three.js, Recharts, Lucide React.

**Storage**: PostgreSQL 16 (Relational tables + JSONB for agent runs, observations, hypotheses, and fingerprints).

**Testing**: `pytest`, `pytest-asyncio`, `pytest-mock`, `httpx` (Backend API, safety policy, agent schemas, and E2E workflow tests); `vitest` / React Testing Library (Frontend UI component tests).

**Target Platform**: Google Cloud Run (Containerized FastAPI backend & static/containerized React frontend), Cloud SQL for PostgreSQL.

**Project Type**: Web Application (Modular monolith backend + Single-Page Application frontend).

**Performance Goals**: Sub-5s incident detection, sub-30s initial diagnosis, sub-90s autonomous resolution, 1 Hz real-time telemetry streaming, 60 fps 3D globe rendering on standard laptops.

**Constraints**: Bounded 3-day hackathon execution scope, zero privileged tool access in frontend, deterministic Safety Director governance, reproducible 3-minute demo path.

**Scale/Scope**: 1 unified modular backend, 1 responsive Command Center UI, 5 specialist agents, 10 normalized PostgreSQL entities, 1 end-to-end reproducible live sports final scenario ("India vs Australia Final").

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check Item | Status | Justification |
|-----------|------------|--------|---------------|
| **1. Real Agentic System** | Distinct specialist agents (Incident Commander, Observability, Business Impact, Remediation, Verification)? | **PASS** | 5 separate agent modules with dedicated Pydantic I/O contracts. |
| **2. Hierarchical Supervisor** | Supervisor orchestrates specialists via shared state? | **PASS** | Incident Commander state machine governs workflow; no direct peer-to-peer bypass. |
| **3. Gemini is Reasoning** | LLM reasons (evidence, hypotheses, summaries); deterministic code handles safety & policy? | **PASS** | Safety Director and state machine in pure Python code; Gemini handles reasoning and correlation. |
| **4. Google Cloud Runtime** | Genuine use of Google Cloud agent runtime & Gemini? | **PASS** | Built with Google GenAI SDK / ADK deployable to Cloud Run with Vertex AI. |
| **5. Grafana Integration** | Runtime Grafana MCP client querying metrics, logs, traces? | **PASS** | Formal MCP JSON-RPC integration defined in `mcp-contract.md`. |
| **6. Media & Entertainment** | Centered on live streaming broadcast failure? | **PASS** | "India vs Australia Final" scenario with transcoder, viewer concurrency, and ad window metrics. |
| **7. Closed-Loop Autonomy** | Observe → Investigate → Correlate → Assess → Decide → Govern → Act → Verify → Resolve? | **PASS** | Full 11-step lifecycle implemented with automated retry ceiling. |
| **8. Actual Remediation** | Real controlled operational action (e.g. traffic shift)? | **PASS** | Regional traffic shift executed against live video routing proxy API. |
| **9. Independent Verification** | Verification Agent queries telemetry post-action before resolving? | **PASS** | Verification Agent queries metrics for 15s before transitioning to `RESOLVED`. |
| **10. Safety by Design** | Deterministic Safety Director evaluating blast radius and risk? | **PASS** | Allowlisted actions with `AUTO_EXECUTE` vs `HUMAN_APPROVAL_REQUIRED` gates. |
| **11. Persistent System of Record** | PostgreSQL stores all incidents, runs, transitions, and fingerprints? | **PASS** | 10 normalized tables with SQLAlchemy 2.x asyncpg models. |
| **12. Explainability** | Concise evidence-based explanations without exposing raw CoT? | **PASS** | Structured schemas enforce clean evidence summaries and confidence ratings. |
| **13. Enterprise Security** | Least privilege, server-side credentials, Secret Manager ready? | **PASS** | Backend-mediated tools, no secrets in frontend. |
| **14. UI/UX Quality** | Cinematic broadcast operations dashboard with purposeful 3D? | **PASS** | React Three Fiber spatial globe visualizing live node health in 10-second glanceable layout. |
| **15. Functionality over Complexity** | Single deployable backend modular monolith? | **PASS** | No microservice sprawl, single FastAPI container. |
| **16. Demo-First Engineering** | Deterministic 3-minute reproducible demo? | **PASS** | Scenario Simulator injects repeatable degradation with 1-click execution. |
| **17. Hackathon Compliance** | Open-source license, public repo, reproducible demo, 3-min video? | **PASS** | Fully planned in deliverables. |
| **18. Testability** | Automated tests for policies, schemas, workflow, and happy-path? | **PASS** | Pytest suite with `test_e2e_workflow.py`. |
| **19. Observability of Agents** | Real-time timeline of agent runs, durations, and tool calls? | **PASS** | SSE event stream publishing all transitions to frontend. |
| **20. Winner-Level Product** | Feels like an autonomous live media Incident Director? | **PASS** | Tailored specifically to broadcast operations center workflows. |

## Project Structure

### Documentation (this feature)

```text
specs/001-media-incident-director/
├── spec.md              # Feature specification
├── plan.md              # This implementation plan
├── research.md          # Technical research & decisions (Phase 0)
├── data-model.md        # Database schema & entity definitions (Phase 1)
├── quickstart.md        # Local setup & E2E validation guide (Phase 1)
├── contracts/           # Interface contracts (Phase 1)
│   ├── api-spec.yaml    # OpenAPI 3.1 REST & SSE specification
│   ├── agent-schemas.md # Pydantic v2 specialist agent contracts
│   └── mcp-contract.md  # Grafana MCP tool definitions
└── checklists/
    └── requirements.md  # Spec quality validation checklist
```

### Source Code (repository root)

```text
backend/
├── alembic/                      # Database migrations
│   ├── env.py
│   └── versions/
├── src/
│   ├── main.py                   # FastAPI entrypoint & SSE router
│   ├── config.py                 # Pydantic v2 settings & environment
│   ├── api/                      # REST endpoints (incidents, approval, demo)
│   │   ├── incidents.py
│   │   ├── approvals.py
│   │   ├── stream.py
│   │   └── demo.py
│   ├── agents/                   # Google Cloud ADK / Gemini specialist agents
│   │   ├── base.py
│   │   ├── commander.py          # Supervisor agent
│   │   ├── investigator.py       # Observability Investigator (Grafana MCP)
│   │   ├── impact.py             # Business Impact Agent
│   │   ├── remediation.py        # Controlled Remediation Agent
│   │   └── verifier.py           # Telemetry Verification Agent
│   ├── orchestration/            # Deterministic state machine & workflow engine
│   │   ├── engine.py
│   │   └── states.py
│   ├── policy/                   # Deterministic Safety Director
│   │   ├── director.py
│   │   └── rules.py
│   ├── integrations/             # External client abstractions
│   │   ├── grafana_mcp.py        # Grafana MCP Client (Prometheus, Loki, Tempo)
│   │   ├── mock_grafana.py       # Deterministic mock MCP provider for local dev
│   │   └── vertex_memory.py      # Vertex AI Search / historical fingerprint store
│   ├── persistence/              # SQLAlchemy 2.x models & repository layer
│   │   ├── database.py
│   │   ├── models.py
│   │   └── repository.py
│   ├── simulator/                # In-process live media streaming simulator
│   │   ├── media_env.py          # Transcoder & playback state
│   │   └── injector.py           # "India vs Australia Final" scenario injector
│   └── events/                   # In-process pub/sub event bus for real-time SSE
│       └── bus.py
├── tests/
│   ├── unit/                     # Policy rules, simulator, Pydantic schemas
│   ├── integration/              # Database persistence, Grafana MCP mock, agent runs
│   └── e2e/
│       └── test_e2e_workflow.py  # Complete closed-loop incident lifecycle test
├── Dockerfile
├── requirements.txt
└── alembic.ini

frontend/
├── src/
│   ├── main.tsx                  # React entrypoint
│   ├── App.tsx                   # Main layout & router
│   ├── components/
│   │   ├── command-center/       # Primary dashboard layout
│   │   │   ├── Header.tsx        # Event status & 10-second glance banner
│   │   │   ├── TelemetryGrid.tsx # Real-time charts (playback error, latency, GPU)
│   │   │   ├── AgentTimeline.tsx # Multi-agent execution timeline
│   │   │   ├── RootCauseCard.tsx # Diagnostic hypothesis & evidence
│   │   │   ├── BusinessCard.tsx  # Impact dials (viewers, ad window, SLA)
│   │   │   └── SafetyModal.tsx   # Human approval modal with blast radius
│   │   ├── canvas3d/             # Lightweight React Three Fiber visualization
│   │   │   ├── BroadcastCore.tsx # Central live broadcast sphere
│   │   │   ├── ServiceNodes.tsx  # Regional transcoders & edge nodes
│   │   │   └── SceneCanvas.tsx   # Canvas container & lighting
│   │   └── simulator/
│   │       └── SimulatorBar.tsx  # Demo scenario trigger & reset controls
│   ├── hooks/
│   │   ├── useEventStream.ts     # SSE connection & real-time state sync
│   │   └── useIncident.ts        # REST queries & approval mutations
│   ├── types/                    # TypeScript interfaces matching backend models
│   │   └── incident.ts
│   └── styles/
│       └── index.css             # Cinematic dark theme tokens
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json

docker-compose.yml                # PostgreSQL 16 & optional local Grafana container
README.md                         # Project overview, architecture, & hackathon guide
ARCHITECTURE.md                   # Detailed multi-agent & Grafana MCP design
SECURITY.md                       # Enterprise security & safety governance
DEMO.md                           # 3-minute judge reproduction script
.env.example                      # Environment variables template
LICENSE                           # Apache 2.0 Open Source License
```

**Structure Decision**: Selected a clear **Modular Monolith** pattern: `backend/` encapsulates all agent, policy, integration, simulator, and persistence logic in a single deployable Python service, while `frontend/` provides the real-time React + Three.js Command Center.

## Complexity Tracking

> **Constitution Check passed 100% with 0 unjustified violations.**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *None* | N/A | Fully complies with all 20 principles and single-backend modular architecture. |
