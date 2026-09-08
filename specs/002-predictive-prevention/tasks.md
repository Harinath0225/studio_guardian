# Implementation Tasks: Predictive Prevention & Proactive Remediation

**Feature**: [`specs/002-predictive-prevention/spec.md`](file:///c:/Coding_learning/studio_guardian/studio_guardian/specs/002-predictive-prevention/spec.md)
**Plan**: [`specs/002-predictive-prevention/plan.md`](file:///c:/Coding_learning/studio_guardian/studio_guardian/specs/002-predictive-prevention/plan.md)
**Status**: Ready for Implementation

---

## Phase 1: Setup (Shared Infrastructure & Configuration)

**Purpose**: Project configuration, domain models, and API schemas.

- [x] T001 Define predictive configuration settings and feature weights in `backend/src/config.py`
- [x] T002 [P] Create prediction API request/response schemas in `backend/src/prediction/schemas.py`
- [x] T003 [P] Define TypeScript interfaces for predictive state, contributors, and proposals in `frontend/src/types/prediction.ts`

---

## Phase 2: Foundational (Data Persistence & Telemetry Ingestion)

**Purpose**: Core infrastructure, database schemas, feature normalizer, and risk model that MUST be complete before user stories begin.

**⚠️ CRITICAL**: Blocking prerequisites for all predictive user stories.

- [x] T004 Add 6 relational predictive entities (`predictive_snapshots`, `prediction_evidence`, `prediction_decisions`, `prevention_actions`, `prevention_verifications`, `prediction_fingerprints`) to `backend/src/persistence/models.py`
- [x] T005 Implement predictive repository CRUD operations in `backend/src/persistence/predictive_repository.py`
- [x] T006 Ensure database migrations and startup auto-creation support new predictive tables in `backend/src/persistence/database.py`
- [x] T007 Extend Grafana MCP client with predictive telemetry queries (`query_prometheus_metrics`, `search_loki_logs`, `list_grafana_alerts`) in `backend/src/integrations/grafana.py`
- [x] T008 [P] Persist raw telemetry observations, query expressions, timestamps, and durations into `prediction_evidence` in `backend/src/integrations/grafana.py`
- [x] T009 [P] Extend high-fidelity local mock telemetry provider for predictive load surge in `backend/src/integrations/mock_grafana.py`
- [x] T010 Implement SLO min-max clamping normalizer in `backend/src/prediction/feature_normalizer.py`
- [x] T011 Implement 60-second sliding-window linear regression slope and acceleration calculation in `backend/src/prediction/feature_normalizer.py`
- [x] T012 Implement baseline deviation and rate-of-change calculators in `backend/src/prediction/feature_normalizer.py`
- [x] T013 [P] Write deterministic unit tests for feature normalizer in `backend/tests/unit/test_feature_normalizer.py`
- [x] T014 Implement weighted risk scoring engine and contributor breakdown in `backend/src/prediction/risk_model.py`
- [x] T015 Implement operational risk levels (`HEALTHY`, `WATCH`, `ELEVATED`, `HIGH`, `IMMINENT`) and threshold bounds in `backend/src/prediction/thresholds.py`
- [x] T016 Implement deterministic time-to-threshold window calculation in `backend/src/prediction/predictor.py`
- [x] T017 Implement independent confidence scoring (freshness, completeness, signal concordance) in `backend/src/prediction/predictor.py`
- [x] T018 [P] Write deterministic unit tests for risk model and predictor in `backend/tests/unit/test_risk_model.py`

**Checkpoint**: Foundation ready — predictive agent, governance, and user story implementation can begin.

---

## Phase 3: User Story 1 - Autonomous Proactive Prevention of Transcoder Saturation (Priority: P1) 🎯 MVP

**Goal**: Deliver end-to-end autonomous prevention: detect emerging transcoder saturation, evaluate risk $\ge 0.80$, autonomously scale capacity, and verify stream continuity without human intervention.

**Independent Test**: Send telemetry exhibiting accelerating transcoder utilization. The system transitions to `IMMINENT RISK`, auto-executes `scale_transcoder_pool`, drops GPU below 65%, and verifies stream continuity with zero playback error spikes.

### Tests for User Story 1

- [x] T019 [P] [US1] Write unit test for Predictive Risk Agent structured output in `backend/tests/unit/test_predictive_agent.py`
- [x] T020 [P] [US1] Write unit test for autonomous safety gating in `backend/tests/unit/test_predictive_safety.py`

### Implementation for User Story 1

- [x] T021 [US1] Implement `PredictiveRiskAgent` connecting to Grafana MCP, predictor, and Gemini in `backend/src/agents/predictive_risk_agent.py`
- [x] T022 [US1] Implement Gemini structured prompt for failure hypothesis, contributing factors, and uncertainty in `backend/src/agents/predictive_risk_agent.py`
- [x] T023 [US1] Persist agent execution frames, session metadata, and runtime tags in `backend/src/agents/predictive_risk_agent.py`
- [x] T024 [US1] Extend `IncidentCommander` with predictive workflow states (`MONITORING`, `RISK_DETECTED`, `PREDICTING`, `POLICY_CHECK`) in `backend/src/agents/incident_commander.py`
- [x] T025 [US1] Extend `SafetyDirector` with deterministic criteria (risk $\ge 0.80$, confidence $\ge 0.85$, blast radius $\le 20\%$, allowlist) in `backend/src/agents/safety_director.py`
- [x] T026 [US1] Extend `media_env.py` to support load-surge progression and controlled capacity expansion (`scale_transcoder_pool`) in `backend/src/simulator/media_env.py`
- [x] T027 [US1] Implement allowlisted preventive capacity scaling action in `backend/src/agents/remediation_agent.py`
- [x] T028 [US1] Implement REST endpoints for `/api/v1/prediction/status` and `/api/v1/prediction/evaluate` in `backend/src/api/prediction.py`
- [x] T029 [US1] Emit `PREDICTIVE_SNAPSHOT`, `PREDICTION_DECISION`, and `PREVENTION_PROPOSAL` over SSE in `backend/src/api/stream.py`
- [x] T030 [US1] Mount prediction router in `backend/src/main.py`
- [x] T031 [P] [US1] Implement frontend prediction API client in `frontend/src/services/predictionApi.ts`
- [x] T032 [P] [US1] Create `RiskTrajectoryCard` rendering gauge and animated risk score trend in `frontend/src/components/command-center/RiskTrajectoryCard.tsx`
- [x] T033 [P] [US1] Create `PredictionCard` rendering failure mode, hypothesis, and window in `frontend/src/components/command-center/PredictionCard.tsx`
- [x] T034 [P] [US1] Create `ContributingFactorsCard` displaying points breakdown in `frontend/src/components/command-center/ContributingFactorsCard.tsx`
- [x] T035 [US1] Implement primary `PredictiveDashboard` view in `frontend/src/components/command-center/PredictiveDashboard.tsx`
- [x] T036 [US1] Add Predictive Operations mode switcher to `frontend/src/components/command-center/Header.tsx`
- [x] T037 [US1] Extend 3D `ServiceNodes` with transcoder stress shaders and capacity expansion particles in `frontend/src/components/canvas3d/ServiceNodes.tsx`
- [x] T038 [US1] Mount `PredictiveDashboard` and wire SSE event listeners in `frontend/src/App.tsx`

**Checkpoint**: User Story 1 (MVP) is fully functional and testable independently.

---

## Phase 4: User Story 2 - Governed Preventive Remediation with Human Approval (Priority: P2)

**Goal**: Provide human-in-the-loop governance for preventive actions exceeding $20\%$ blast radius or confidence $< 85\%$, displaying economic loss vs. cost trade-offs and enabling one-click authorization.

**Independent Test**: Trigger an emerging regional bottleneck where the proposed action exceeds $20\%$ blast radius. Verify that execution halts at `WAITING_HUMAN_APPROVAL`, displays the economics briefing, and executes only upon operator confirmation.

### Tests for User Story 2

- [x] T039 [P] [US2] Write unit test for human approval branch gating in `backend/tests/unit/test_human_approval_gate.py`

### Implementation for User Story 2

- [x] T040 [US2] Implement prevention economics calculator (`expected_loss`, `prevention_cost`, `expected_avoided_exposure`) in `backend/src/agents/business_impact_agent.py`
- [x] T041 [US2] Extend `SafetyDirector` to branch to `WAITING_HUMAN_APPROVAL` when blast radius $> 20\%$ or confidence $< 0.85$ in `backend/src/agents/safety_director.py`
- [x] T042 [US2] Implement REST endpoints for `/api/v1/prediction/proposals/{id}/authorize` and `/reject` in `backend/src/api/prediction.py`
- [x] T043 [US2] Persist operator identity, approval timestamp, and notes to `prevention_actions` in `backend/src/persistence/predictive_repository.py`
- [x] T044 [P] [US2] Create `PreventionEconomicsCard` rendering expected loss vs. scale cost trade-off in `frontend/src/components/command-center/PreventionEconomicsCard.tsx`
- [x] T045 [US2] Extend `SafetyModal` to display prediction briefing, economics trade-off, and one-click authorization in `frontend/src/components/command-center/SafetyModal.tsx`
- [x] T046 [US2] Wire operator authorization and rejection handlers in `frontend/src/components/command-center/PredictiveDashboard.tsx`

**Checkpoint**: User Stories 1 and 2 are both functional and testable independently.

---

## Phase 5: User Story 3 - Independent Post-Prevention Verification & Counterfactual Accounting (Priority: P3)

**Goal**: Prove that preventive actions worked by querying post-action telemetry, calculating before/after deltas, indexing predictive fingerprints to memory, and presenting avoided exposure estimates.

**Independent Test**: After preventive capacity scaling completes, verify that the Verification Agent re-queries Grafana MCP, confirms $\Delta \text{GPU} \le -25\%$ and risk $< 25$, records the fingerprint, and displays avoided commercial exposure.

### Tests for User Story 3

- [x] T047 [P] [US3] Write unit test for independent telemetry delta verification in `backend/tests/unit/test_verification_agent.py`

### Implementation for User Story 3

- [x] T048 [US3] Extend `VerificationAgent` to re-query Grafana MCP 30s and 60s post-action in `backend/src/agents/verification_agent.py`
- [x] T049 [US3] Calculate telemetry differentials ($\Delta \text{GPU}$, $\Delta \text{latency}$, $\Delta \text{risk}$) and enforce recovery criteria ($\Delta \text{GPU} \le -25\%$, $\text{risk} < 25$) in `backend/src/agents/verification_agent.py`
- [x] T050 [US3] Persist verification audit record and counterfactual avoided loss to `prevention_verifications` in `backend/src/persistence/predictive_repository.py`
- [x] T051 [US3] Index successful preventive fingerprint to `prediction_fingerprints` table in `backend/src/persistence/predictive_repository.py`
- [x] T052 [US3] Implement historical memory matching to surface prior interventions in `backend/src/integrations/vertex_memory.py`
- [x] T053 [US3] Emit `PREVENTION_VERIFIED` SSE event over stream in `backend/src/api/stream.py`
- [x] T054 [P] [US3] Create `VerificationResultCard` rendering before/after metric comparison and net avoided exposure in `frontend/src/components/command-center/VerificationResultCard.tsx`
- [x] T055 [P] [US3] Create `PredictiveMemoryCard` surfacing past matching interventions in `frontend/src/components/command-center/PredictiveMemoryCard.tsx`
- [x] T056 [US3] Update 3D `ServiceNodes` to transition back to healthy emerald green upon verification in `frontend/src/components/canvas3d/ServiceNodes.tsx`

**Checkpoint**: User Stories 1, 2, and 3 are all independently functional.

---

## Phase 6: User Story 4 - Seamless Fallback from Predictive Watch to Reactive Incident Management (Priority: P4)

**Goal**: Guarantee system resilience: if an emerging incident is unpreventable, rejected, or sudden, seamlessly transition to reactive incident response while carrying over all prior telemetry and candidate root-cause hypotheses.

**Independent Test**: Inject an acute playback failure while in predictive monitoring mode. Verify automatic flip to reactive mode in $<500\text{ms}$ with prior telemetry pre-populated in the reactive incident timeline.

### Tests for User Story 4

- [x] T057 [P] [US4] Write integration test for predictive-to-reactive context inheritance in `backend/tests/integration/test_reactive_fallback.py`

### Implementation for User Story 4

- [x] T058 [US4] Implement seamless context inheritance in `IncidentCommander` when playback error $> 2.0\%$ in `backend/src/agents/incident_commander.py`
- [x] T059 [US4] Promote predictive snapshots, Grafana MCP query cache, and candidate root-cause hypotheses directly to reactive incident record in `backend/src/persistence/repository.py`
- [x] T060 [US4] Implement `UnifiedRuntimeLedger` displaying chronological `[Vertex AI Agent Engine]`, `[Grafana MCP]`, and `[Safety Policy]` execution cards in `frontend/src/components/command-center/UnifiedRuntimeLedger.tsx`
- [x] T061 [US4] Add expandable PromQL/LogQL query parameters and sanitized result inspect drawer in `frontend/src/components/command-center/UnifiedRuntimeLedger.tsx`
- [x] T062 [US4] Implement seamless dashboard view auto-switching upon reactive escalation in `frontend/src/App.tsx`

**Checkpoint**: All 4 user stories are functional and provide complete dual-mode continuity.

---

## Phase 7: Polish, Testing, Demo & Documentation

**Purpose**: Verification, end-to-end demo driver, test coverage, and documentation.

- [x] T063 [P] Implement deterministic multi-step predictive demo driver endpoint (`POST /api/v1/prediction/demo/scenario`) in `backend/src/api/prediction.py`
- [x] T064 [P] Write comprehensive predictive engine unit test suite in `backend/tests/unit/test_predictive_engine.py`
- [x] T065 [P] Write comprehensive safety policy test suite in `backend/tests/unit/test_predictive_safety.py`
- [x] T066 [P] Write agent integration test suite in `backend/tests/integration/test_predictive_agents.py`
- [x] T067 Execute quickstart end-to-end validation script in `scripts/verify_environment.ps1`
- [x] T068 [P] Create `docs/PREDICTIVE.md` detailing the mathematical risk model, normalization formulas, and confidence scoring
- [x] T069 [P] Document real vs. mock Grafana MCP path and provider toggle in `docs/PREDICTIVE.md`
- [x] T070 [P] Document Google Cloud Vertex AI Agent Engine integration, session metadata, and runtime tags in `docs/PREDICTIVE.md`
- [x] T071 Document operational limitations, uncertainty communication, and counterfactual estimation methodology in `docs/PREDICTIVE.md`
- [x] T072 Update root `ARCHITECTURE.md` with the expanded 6-agent predictive hierarchy and state machine

---

## Dependencies & Execution Order

### Phase Dependencies
1. **Phase 1: Setup**: Can start immediately; no dependencies.
2. **Phase 2: Foundational**: Depends on Phase 1 completion; **BLOCKS all user stories**.
3. **Phase 3: User Story 1 (P1 - MVP)**: Depends on Phase 2; implements autonomous prevention core.
4. **Phase 4: User Story 2 (P2)**: Depends on Phase 2 & Phase 3 (extends Safety Director & Business Impact).
5. **Phase 5: User Story 3 (P3)**: Depends on Phase 3 (extends Verification Agent & persistence).
6. **Phase 6: User Story 4 (P4)**: Depends on Phase 3 (wires context inheritance & Unified Ledger).
7. **Phase 7: Polish & Documentation**: Runs after user stories to complete test coverage and docs.

### Parallel Opportunities
- In Phase 1: `T002` and `T003` can run in parallel with `T001`.
- In Phase 2: `T008`, `T009`, `T013`, and `T018` can run in parallel.
- In Phase 3: Frontend card components (`T031`, `T032`, `T033`, `T034`) can run in parallel with backend endpoints.
- In Phase 7: Documentation tasks (`T068`, `T069`, `T070`) and unit tests (`T064`, `T065`, `T066`) can run in parallel.

---

## Implementation Strategy

### MVP Delivery (User Story 1 Only)
1. Complete Phase 1 (Setup) and Phase 2 (Foundational).
2. Implement Phase 3 (User Story 1):
   - `PredictiveRiskAgent` + Deterministic Risk Engine + Autonomous `scale_transcoder_pool` + `PredictiveDashboard`.
3. **Validate**: Trigger load surge and verify autonomous prevention before viewer disruption occurs.

### Incremental Feature Expansion
1. Add Phase 4 (User Story 2) for gated high-blast actions and prevention economics.
2. Add Phase 5 (User Story 3) for independent verification deltas and memory indexing.
3. Add Phase 6 (User Story 4) for reactive fallback and Unified Ledger.
4. Complete Phase 7 for documentation and full regression test suite.
