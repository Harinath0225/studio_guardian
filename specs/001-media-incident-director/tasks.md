# Implementation Tasks: Studio Guardian — Autonomous Live Media Incident Director

**Feature**: `001-media-incident-director`  
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Contracts**: [contracts/](./contracts/)  
**Status**: Ready for Implementation  

---

## Phase 1: Foundation

**Purpose**: Core repository scaffolding, backend/frontend initialization, Docker, and CI basics.

- [x] T001 Initialize repository layout (`backend/`, `frontend/`, `docs/`, `scripts/`) per plan in repository root
- [x] T002 [P] Create Docker Compose environment with PostgreSQL 16 and Grafana MCP service in `docker-compose.yml`
- [x] T003 [P] Initialize Python FastAPI backend structure with `backend/requirements.txt` and `backend/src/config.py`
- [x] T004 [P] Initialize React + TypeScript + Vite frontend with TailwindCSS in `frontend/package.json` and `frontend/vite.config.ts`
- [x] T005 Setup environment variable configuration template in `.env.example`
- [x] T006 Initialize Alembic migrations environment in `backend/alembic.ini` and `backend/alembic/env.py`
- [x] T007 [P] Configure GitHub Actions CI workflow for backend tests and frontend type-checking in `.github/workflows/ci.yml`

---

## Phase 2: Database

**Purpose**: Normalized relational entities, JSONB fields, Alembic migrations, and demo seed data.

- [x] T008 Implement database engine and session factory with SQLAlchemy 2.x asyncpg in `backend/src/persistence/database.py`
- [x] T009 [P] Implement `Incident` and `IncidentEvent` ORM models in `backend/src/persistence/models.py`
- [x] T010 [P] Implement `AgentRun` and `Observation` ORM models in `backend/src/persistence/models.py`
- [x] T011 [P] Implement `RootCauseHypothesis` and `BusinessImpact` ORM models in `backend/src/persistence/models.py`
- [x] T012 [P] Implement `RemediationAction`, `VerificationResult`, `IncidentFingerprint`, and `AuditLog` ORM models in `backend/src/persistence/models.py`
- [x] T013 Generate and verify initial Alembic migration for all tables in `backend/alembic/versions/001_initial_schema.py`
- [x] T014 Implement repository abstraction for CRUD operations and query helpers in `backend/src/persistence/repository.py`
- [x] T014b [P] Implement Incident REST endpoints (`GET /api/v1/incidents`, `GET /api/v1/incidents/{id}`) in `backend/src/api/incidents.py`
- [x] T015 Create deterministic seed data script for historical incidents in `backend/src/persistence/seed.py`

---

## Phase 3: Event Simulator

**Purpose**: In-process media streaming simulation exposing healthy, incident, and recovered states with telemetry generation.

- [x] T016 Implement media stream state machine (`HEALTHY`, `DEGRADED`, `RECOVERED`) in `backend/src/simulator/media_env.py`
- [x] T017 Implement synthetic telemetry generator producing metrics and expose standard Prometheus scrape endpoint at `/metrics` in `backend/src/simulator/metrics_generator.py`
- [x] T018 Implement "India vs Australia Final" deterministic incident injector in `backend/src/simulator/injector.py`
- [x] T019 Implement simulation control endpoints (`POST /api/v1/demo/incident`, `POST /api/v1/demo/reset`, `POST /api/v1/demo/force-failure`) in `backend/src/api/demo.py`
- [x] T020 [P] Write unit tests for simulator state transitions and metric generators in `backend/tests/unit/test_simulator.py`

---

## Phase 4: Google Gemini Agent Foundation

**Purpose**: Integrate the official Google GenAI SDK / Agent Development Kit (ADK) and verify minimal Gemini execution.

- [x] T021 Configure Google GenAI SDK client and Vertex AI credentials in `backend/src/integrations/google_genai.py`
- [x] T022 Implement base agent interface with Pydantic v2 structured output enforcement in `backend/src/agents/base.py`
- [x] T023 Create minimal smoke-test agent running Gemini 2.5 with structured schema in `backend/src/agents/smoke_agent.py`
- [x] T024 Write verification test validating live or mock Gemini structured output execution in `backend/tests/unit/test_gemini_foundation.py`

---

## Phase 5: Grafana MCP Runtime Integration

**Purpose**: Official Model Context Protocol (MCP) client connecting to Grafana for metrics, logs, traces, and alerts.

- [x] T025 Implement Grafana MCP provider abstraction and settings in `backend/src/integrations/grafana_mcp.py`
- [x] T026 Implement JSON-RPC / SSE client transport for Grafana MCP in `backend/src/integrations/mcp_client.py`
- [x] T027 [P] Implement `query_prometheus_metrics` and `search_loki_logs` tool adapters in `backend/src/integrations/mcp_tools.py`
- [x] T028 [P] Implement `get_tempo_traces` and `list_grafana_alerts` tool adapters in `backend/src/integrations/mcp_tools.py`
- [x] T029 Implement high-fidelity local mock MCP server for offline hackathon development in `backend/src/integrations/mock_grafana.py`
- [x] T030 Verify authentic runtime MCP tool calls against running Grafana MCP server with automated test in `backend/tests/integration/test_grafana_mcp.py`

---

## Phase 6: Observability Investigator Agent

**Purpose**: Multi-signal telemetry investigation, deployment correlation, and root-cause hypothesis generation.

- [x] T031 [US2] Implement `InvestigationInput` and `InvestigationReport` schemas in `backend/src/agents/schemas.py`
- [x] T032 [US2] Implement Observability Investigator agent invoking Grafana MCP tools in `backend/src/agents/investigator.py`
- [x] T033 [US3] Implement evidence correlation and root-cause hypothesis ranking using Gemini reasoning in `backend/src/agents/investigator.py`
- [x] T034 [US2] Write unit and integration tests for Observability Investigator with mock telemetry in `backend/tests/unit/test_investigator.py`

---

## Phase 7: Business Impact Agent

**Purpose**: Deterministic live media impact calculation with Gemini natural-language executive explanations.

- [x] T035 [US4] Implement `BusinessImpactInput` and `BusinessImpactAssessment` schemas in `backend/src/agents/schemas.py`
- [x] T036 [US4] Implement deterministic impact calculation engine (viewers affected, VIPs, ad window risk, SLA penalty) in `backend/src/agents/impact.py`
- [x] T037 [US4] Integrate Gemini reasoning to generate concise executive narrative and business summary in `backend/src/agents/impact.py`
- [x] T038 [US4] Write unit tests verifying business impact formulas and boundary conditions in `backend/tests/unit/test_business_impact.py`

---

## Phase 8: Remediation Agent

**Purpose**: Controlled operational candidate selection, parameter evaluation, and live video routing API dispatch.

- [x] T039 [US6] Implement candidate remediation selection schemas in `backend/src/agents/schemas.py`
- [x] T040 [US6] Implement live video routing proxy service exposing standalone HTTP traffic-shifting endpoint (`/route`) in `backend/src/simulator/video_proxy.py`
- [x] T041 [US6] Implement Remediation Agent dispatching regional traffic shift in `backend/src/agents/remediation.py`
- [x] T042 [US6] Write unit tests for remediation dispatch and error handling in `backend/tests/unit/test_remediation.py`

---

## Phase 9: Safety Director

**Purpose**: Deterministic policy engine evaluating confidence, blast radius, risk, and authorization.

- [x] T043 [US5] Implement policy rule definitions and allowlisted actions (`TRAFFIC_SHIFT`, `CONTAINER_RESTART`, `SCALE_REPLICAS`) in `backend/src/policy/rules.py`
- [x] T044 [US5] Implement deterministic Safety Director evaluating blast radius (>25% rule) and diagnostic confidence in `backend/src/policy/director.py`
- [x] T045 [US5] Implement `AUTO_EXECUTE` vs `HUMAN_APPROVAL_REQUIRED` policy gating in `backend/src/policy/director.py`
- [x] T046 [US5] Implement operator approval/rejection endpoints (`POST /api/v1/incidents/{id}/approve`) in `backend/src/api/approvals.py`
- [x] T047 [US5] Write comprehensive unit tests for all safety policy scenarios in `backend/tests/unit/test_safety_policy.py`

---

## Phase 10: Verification Agent

**Purpose**: Independent post-remediation telemetry query, stabilization window comparison, and recovery verdict.

- [x] T048 [US7] Implement `VerificationInput` and `VerificationVerdict` schemas in `backend/src/agents/schemas.py`
- [x] T049 [US7] Implement Verification Agent querying Grafana MCP metrics post-action in `backend/src/agents/verifier.py`
- [x] T050 [US7] Implement before/after delta calculation and stability window evaluation in `backend/src/agents/verifier.py`
- [x] T051 [US8] Implement recovery failure detection routing to re-investigation in `backend/src/agents/verifier.py`
- [x] T052 [US7] Write unit tests for successful recovery, failed recovery, and flapping metrics in `backend/tests/unit/test_verifier.py`

---

## Phase 11: Incident Commander (Supervisor Orchestrator)

**Purpose**: Complete hierarchical state machine orchestrating all specialist agents with persistent transitions.

- [x] T053 [US2] Implement workflow state enum and transition matrix in `backend/src/orchestration/states.py`
- [x] T054 [US2] Implement Incident Commander supervisory state machine in `backend/src/orchestration/engine.py`
- [x] T055 [US2] Implement retry counter and automatic transition to `ESCALATED_HUMAN_TAKEOVER` when max retries exceeded in `backend/src/orchestration/engine.py`
- [x] T056 [US2] Persist every state transition, agent run, and audit log to PostgreSQL during orchestration in `backend/src/orchestration/engine.py`
- [x] T057 [US2] Write workflow integration test verifying end-to-end multi-agent execution in `backend/tests/integration/test_orchestration.py`

---

## Phase 12: Incident Memory

**Purpose**: Fingerprint generation, historical pattern indexing, and previous successful remediation lookup.

- [x] T058 [US9] Implement symptom signature vector extraction in `backend/src/agents/memory.py`
- [x] T059 [US9] Implement historical fingerprint storage and similarity lookup via PostgreSQL in `backend/src/persistence/fingerprints.py`
- [x] T060 [US9] Implement Vertex AI Search client adapter with automatic PostgreSQL full-text/JSONB fallback in `backend/src/integrations/vertex_memory.py`
- [x] T061 [US9] Write unit tests for incident fingerprint matching and recall in `backend/tests/unit/test_incident_memory.py`

---

## Phase 13: Real-Time Backend Events

**Purpose**: Server-Sent Events (SSE) stream publishing 1 Hz telemetry and agent progression.

- [x] T062 [US11] Implement in-process asynchronous pub/sub event bus in `backend/src/events/bus.py`
- [x] T063 [US11] Implement SSE event streaming endpoint (`GET /api/v1/stream/events`) in `backend/src/api/stream.py`
- [x] T064 [US11] Wire orchestrator state changes and telemetry updates into the event bus in `backend/src/orchestration/engine.py`
- [x] T065 [US11] Write test validating SSE event broadcast upon state transition in `backend/tests/unit/test_events.py`

---

## Phase 14: Frontend Design System & Layout

**Purpose**: Cinematic dark-mode broadcast design system, typography, cards, and responsive shell.

- [x] T066 [US11] Configure TailwindCSS color palette, fonts (Inter/Outfit), and glassmorphism utilities in `frontend/tailwind.config.js` and `frontend/src/styles/index.css`
- [x] T067 [P] [US11] Create status badge system (`HEALTHY`, `INVESTIGATING`, `AWAITING_APPROVAL`, `RESOLVED`, `ESCALATED`) in `frontend/src/components/common/StatusBadge.tsx`
- [x] T068 [P] [US11] Create reusable glassmorphic Card container with glowing borders in `frontend/src/components/common/GlassCard.tsx`
- [x] T069 [US11] Build global command center header with live broadcast event status and 10-second glance banner in `frontend/src/components/command-center/Header.tsx`
- [x] T070 [US11] Implement SSE subscription hook with automatic reconnection in `frontend/src/hooks/useEventStream.ts`

---

## Phase 15: 3D Visualization Experience

**Purpose**: Purposeful React Three Fiber spatial globe visualizing live broadcast nodes and incident propagation.

- [x] T071 [US11] Install and configure `@react-three/fiber` and `@react-three/drei` in `frontend/package.json`
- [x] T072 [US11] Implement central "Live Event Core" globe representing live broadcast stream in `frontend/src/components/canvas3d/BroadcastCore.tsx`
- [x] T073 [US11] Implement regional broadcast node meshes (Australia, Singapore, US, EU) with color transitions (cyan → amber/red → emerald) in `frontend/src/components/canvas3d/ServiceNodes.tsx`
- [x] T074 [US11] Implement WebGL canvas container with graceful 2D fallback when WebGL is unavailable in `frontend/src/components/canvas3d/SceneCanvas.tsx`

---

## Phase 16: Main Command Center Dashboard

**Purpose**: Telemetry charts, agent control room, root-cause card, business impact dials, and action controls.

- [x] T075 [US11] Implement real-time telemetry grid using Recharts for playback error rate, transcoder latency, and GPU allocations in `frontend/src/components/command-center/TelemetryGrid.tsx`
- [x] T076 [US2] Implement multi-agent hierarchy control room with active pulse animations and execution timers in `frontend/src/components/command-center/AgentTimeline.tsx`
- [x] T077 [US3] Implement Root Cause Hypothesis card showing confidence bar, causal chain, and correlated evidence tags in `frontend/src/components/command-center/RootCauseCard.tsx`
- [x] T078 [US4] Implement Business Impact card showing affected viewer count, VIP audience, ad window status, and revenue exposure in `frontend/src/components/command-center/BusinessCard.tsx`
- [x] T078b [US5] Implement Autonomy Policy Dial component (Full Autonomy / Assisted / Manual Takeover) in `frontend/src/components/command-center/AutonomyDial.tsx`
- [x] T079 [US9] Implement Historical Incident Memory match card in `frontend/src/components/command-center/IncidentMemoryCard.tsx`
- [x] T080 [US11] Assemble primary dashboard layout integrating all cards, 3D canvas, and timeline in `frontend/src/App.tsx`

---

## Phase 17: Reports & Post-Incident Communication

**Purpose**: Automated generation of role-tailored post-incident summaries.

- [x] T081 [US10] Implement report generation service in `backend/src/services/reports.py`
- [x] T082 [US10] Implement Engineering RCA report template with telemetry deltas and causal chain in `backend/src/templates/rca_report.md`
- [x] T083 [US10] Implement Executive Brief and Customer Communication templates in `backend/src/templates/executive_brief.md`
- [x] T084 [US10] Create report viewer drawer component on frontend in `frontend/src/components/command-center/ReportDrawer.tsx`

---

## Phase 18: Error Handling & Human Approval Modals

**Purpose**: Interactive safety approvals, manual takeovers, and resilient partner failure handling.

- [x] T085 [US5] Implement Human Approval Modal displaying blast radius, risk score, and one-click `APPROVE` / `REJECT` buttons in `frontend/src/components/command-center/SafetyModal.tsx`
- [x] T086 [US11] Implement emergency `MANUAL TAKEOVER` abort button in `frontend/src/components/command-center/ManualOverrideButton.tsx`
- [x] T087 Implement graceful degraded UI states for Grafana or Gemini unreachability in `frontend/src/components/common/DegradedBanner.tsx`
- [x] T088 Write frontend component tests for approval interactions in `frontend/src/tests/SafetyModal.test.tsx`

---

## Phase 19: Comprehensive Testing Suite

**Purpose**: Unit, integration, safety policy, and end-to-end happy-path verification.

- [x] T089 [P] Create full safety policy rule test suite in `backend/tests/unit/test_policy_comprehensive.py`
- [x] T090 [P] Create agent structured schema validation test suite in `backend/tests/unit/test_schemas.py`
- [x] T091 Create full end-to-end happy-path test (`trigger → investigate → impact → decide → policy → remediate → verify → resolve`) in `backend/tests/e2e/test_e2e_workflow.py`
- [x] T092 Create failure path tests (remediation failure, verification failure, retry exhaustion) in `backend/tests/e2e/test_failure_paths.py`

---

## Phase 20: Google Cloud Deployment

**Purpose**: Cloud Run containerization, Cloud SQL configuration, Secret Manager, and deployment docs.

- [x] T093 Create production multi-stage backend container Dockerfile in `backend/Dockerfile`
- [x] T094 Create production frontend build and Nginx container Dockerfile in `frontend/Dockerfile`
- [x] T095 [P] Create Cloud Run deployment script with IAM service identity in `scripts/deploy_cloud_run.sh`
- [x] T096 Document Google Cloud Run, Cloud SQL, and Secret Manager deployment steps in `docs/DEPLOYMENT.md`

---

## Phase 21: Demo Hardening

**Purpose**: Deterministic scenario controls, smooth red-to-green transitions, and judge reproduction scripts.

- [x] T097 Build sticky Demo Control Bar with `Trigger Incident`, `Reset Demo`, and `Force Failure` buttons in `frontend/src/components/simulator/SimulatorBar.tsx`
- [x] T098 Ensure 3D canvas and UI metric transitions transition visibly from green (healthy) to red (incident) and back to green within 90 seconds in `frontend/src/components/canvas3d/SceneCanvas.tsx`
- [x] T099 Write automated demo runner script simulating the complete 3-minute judge flow in `scripts/run_demo.py`

---

## Phase 22: Hackathon Submission Artifacts

**Purpose**: Complete documentation, architecture diagrams, open-source license, and submission package.

- [x] T100 Create comprehensive `README.md` highlighting Google Cloud runtime, Gemini, and Grafana MCP integration
- [x] T101 Create detailed architecture document with ASCII/Mermaid diagrams in `ARCHITECTURE.md`
- [x] T102 Create step-by-step 3-minute judge reproduction script in `DEMO.md`
- [x] T103 Create enterprise security and safety director governance documentation in `SECURITY.md`
- [x] T104 Add Apache 2.0 open-source license in `LICENSE`
- [x] T105 Prepare Devpost submission summary and video script outline in `docs/SUBMISSION.md`

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1 (Foundation)
    │
    ▼
Phase 2 (Database)
    │
    ├──────────────────────┬──────────────────────┐
    ▼                      ▼                      ▼
Phase 3 (Simulator)   Phase 4 (Gemini Base)  Phase 5 (Grafana MCP)
    │                      │                      │
    └──────────────────────┼──────────────────────┘
                           │
                           ▼
Phase 6 (Observability) ──► Phase 7 (Business Impact)
                           │
                           ▼
Phase 8 (Remediation)   ──► Phase 9 (Safety Director)
                           │
                           ▼
Phase 10 (Verification) ──► Phase 11 (Incident Commander)
                           │
                           ├──────────────────────┐
                           ▼                      ▼
Phase 12 (Memory)     Phase 13 (Events SSE)  Phase 14 (Design System)
                           │                      │
                           ▼                      ▼
                     Phase 15 (3D)          Phase 16 (Dashboard)
                           │                      │
                           └──────────────────────┘
                                      │
                                      ▼
Phase 17 (Reports)      ──► Phase 18 (Approvals/Errors)
                                      │
                                      ▼
Phase 19 (Testing)      ──► Phase 20 (Cloud Deploy)
                                      │
                                      ▼
Phase 21 (Hardening)    ──► Phase 22 (Submission)
```

### Parallel Opportunities

- **Phase 1**: T002 (Docker), T003 (FastAPI config), T004 (Vite React), and T007 (CI) can execute in parallel.
- **Phase 2**: T009, T010, T011, and T012 (ORM models) can execute in parallel.
- **Phase 3, 4, 5**: Once Phase 2 completes, Event Simulator (Phase 3), Gemini Foundation (Phase 4), and Grafana MCP (Phase 5) can execute in parallel.
- **Phase 14 & 15**: Frontend Design System and 3D Canvas can be developed in parallel with backend agent phases.
- **Phase 19**: T089 (Policy tests) and T090 (Schema tests) can run in parallel.
- **Phase 22**: All documentation tasks (T100–T105) can execute in parallel.

---

## Implementation Strategy: MVP First

1. **MVP Increment 1 (Phases 1–3)**: Working FastAPI backend with PostgreSQL, synthetic telemetry generator, and deterministic incident injection.
2. **MVP Increment 2 (Phases 4–6)**: Observability Investigator executes live Grafana MCP tool queries and outputs evidence-based root cause hypothesis.
3. **MVP Increment 3 (Phases 7–11)**: Closed-loop supervisor workflow: Business Impact → Safety Director → Remediation → Verification → Resolution.
4. **MVP Increment 4 (Phases 13–16)**: Full Command Center UI with 3D broadcast core, real-time telemetry streaming, and human approval modal.
5. **Release Hardening (Phases 17–22)**: Automated end-to-end tests, Cloud Run deployment, and hackathon submission deliverables.

---

## Phase 23: Convergence

**Purpose**: Address gaps identified during speckit-converge production-readiness and judge-experience audit.

- [x] T106 Mount and wire SafetyModal into `frontend/src/App.tsx` for human approval workflows per FR-017, FR-018 (partial)
- [x] T107 Normalize 3D mesh and node health color states across all active incident lifecycle stages in `frontend/src/components/canvas3d/BroadcastCore.tsx` and `frontend/src/components/canvas3d/ServiceNodes.tsx` per FR-029, SC-007 (partial)
- [x] T108 Implement emergency takeover endpoint in backend and mount ManualOverrideButton in `frontend/src/components/command-center/Header.tsx` per FR-004, Constitution §10 (partial)
- [x] T109 Mount DegradedBanner in `frontend/src/App.tsx` to signal offline mock mode or stream reconnection per US11/AC3 (partial)


