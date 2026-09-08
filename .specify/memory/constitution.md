<!--
Sync Impact Report:
- Version bump: 1.0.0 -> 2.0.0
- Modified principles: Replaced previous 20 principles with 18 newly defined NON-NEGOTIABLE principles focusing heavily on predictive prevention, media domain intelligence, ad integrity, and mathematically traceable data.
- Added sections: None.
- Removed sections: None.
- Follow-up TODOs: None.
-->

# STUDIO GUARDIAN Constitution

## Core Principles

### 1. VERTEX AI IS THE AGENT RUNTIME
Vertex AI Agent Builder / Agent Platform and the appropriate Google Agent Development Kit / Agent Engine integration must visibly participate in the real runtime. The application must NOT be a FastAPI application that merely calls Gemini.

The agent execution path must be demonstrable as:
Application → Vertex AI Agent Runtime → Incident Commander → Specialist Agents → Tools / MCP → Decisions / Actions.

The UI must expose truthful runtime information such as: agent runtime, agent name, current specialist, run/session identifier where available, agent state, and tool execution events. Do not fabricate Vertex AI runtime information.

### 2. GEMINI IS THE REASONING LAYER
Gemini is responsible for: evidence interpretation, correlation, hypothesis generation, recommendation comparison, natural-language explanation, and stakeholder reports. Gemini must not be treated as the source of truth for raw telemetry or deterministic calculations.

### 3. GRAFANA MCP IS THE OPERATIONAL SOURCE OF TRUTH
Grafana is the selected partner track. The primary evidence path must be: Media Environment → telemetry → Grafana → Grafana MCP → Agent.

The application must make genuine runtime calls to Grafana MCP. Relevant telemetry can include: Prometheus metrics, Loki logs, Tempo traces, Grafana alerts, incident information, and dashboard information. The system must preserve source metadata for important evidence.

### 4. MATHEMATICALLY TRACEABLE DATA
Every important numerical claim must have a traceable origin. For predictive and business calculations: RAW GRAFANA VALUE → NORMALIZATION → DERIVED FEATURE → FORMULA → RESULT → GEMINI EXPLANATION. Do not allow Gemini to invent telemetry values, risk scores, financial calculations or verification statistics.

### 5. PREDICT BEFORE FAILURE
The product must support proactive prevention. The primary predictive lifecycle is: MONITOR → DETECT LEADING SIGNALS → CALCULATE RISK → PREDICT → ASSESS IMPACT → GOVERN → PREVENT → VERIFY. The system must distinguish prediction from certainty. Never claim that an avoided incident definitely would have occurred.

### 6. REACTIVE FALLBACK
Prediction must not replace incident response. If user-visible degradation actually occurs: PREDICTION → INCIDENT → INVESTIGATE → REMEDIATE → VERIFY. The predictive and reactive systems must form one closed-loop product.

### 7. MEDIA DOMAIN INTELLIGENCE
The product must reason about real media/entertainment signals and business concerns. Examples include: playback, transcoding, live streaming, SCTE-35, ad insertion, AV synchronization, loudness, dropped frames, regional delivery, viewers, ad windows, sponsor SLA, and business exposure.

### 8. SEMANTIC MEDIA QUALITY
Infrastructure health is not sufficient evidence of media health. The system should be able to detect situations where CPU, Memory, and HTTP are healthy, while media quality is degraded. Examples include: SCTE-35 splice timing drift, ad pod integrity failure, audio/video sync drift, frame drop anomaly, black-frame anomaly, and audio loudness deviation.

### 9. AD INTEGRITY IS BUSINESS CRITICAL
The Ad Integrity Agent may evaluate: SCTE-35 cue timing, splice alignment, ad pod integrity, ad tracking health, and manifest anomalies. A configured operational tolerance must be used. Do not claim regulatory or standards compliance unless an exact applicable specification/profile is verified. Represent thresholds such as "SCTE alignment tolerance = configured operational threshold" rather than presenting arbitrary thresholds as universal standards.

### 10. PERCEPTUAL QUALITY IS A SIGNAL, NOT A FULL QC SYSTEM
Keep perceptual analysis intentionally lightweight. Use a limited set of measurable signals: AV sync offset, loudness deviation, frame/drop ratio, and black-frame ratio. Do not attempt to implement a complete professional broadcast QC platform.

### 11. SAFETY BEFORE AUTONOMY
Autonomous action must pass deterministic policy. Policy inputs include: confidence, risk, blast radius, cost, expected benefit, authorization, and action allowlist. AI cannot bypass Safety Director rules.

### 12. BUSINESS VALUE MUST BE CALCULABLE
Business Impact Agent must use transparent deterministic formulas. 
Expected incident exposure = expected viewer loss + expected advertising loss + SLA exposure.
Preventive value = expected loss without intervention - expected loss after intervention - cost of prevention.
All monetary values must be labeled as estimates.

### 13. BLACK SWAN GAME DAY
The application must provide a deterministic chaos injection facility. The demo must be able to intentionally introduce: transcoder stress, regional delivery degradation, SCTE-35 corruption, and perceptual media quality failure. A judge must be able to trigger a scenario without modifying code.

### 14. COUNTERFACTUAL HONESTY
When prevention succeeds before an actual outage, do NOT say "we saved exactly $142,500." Instead say "Estimated exposure avoided: $142,500." The UI must distinguish between OBSERVED, PREDICTED, ESTIMATED, and VERIFIED.

### 15. CLOSED-LOOP PROOF
Success requires evidence for the complete lifecycle: Grafana evidence → mathematical computation → Gemini reasoning → agent decision → policy decision → remediation → fresh Grafana evidence → verification.

### 16. UX
The interface must communicate an enterprise-grade broadcast operations center. It should be modern, sleek, premium, professional, cinematic, and user-friendly. 3D visualizations must explain the operational system and must never become decorative gimmicks.

### 17. DEMO-FIRST PRIORITY
The system must have one deterministic flagship demo: PREDICT → PREVENT → VERIFY, followed by: INJECT BLACK SWAN → DETECT → INVESTIGATE → REMEDIATE → VERIFY. This demonstrates both proactive and reactive autonomy.

### 18. HACKATHON COMPLIANCE
The implementation must visibly prove: Gemini runtime, Vertex AI Agent Builder / Agent Platform / Agent Engine, Google Cloud runtime, real Grafana MCP, real media workflow, multi-agent orchestration, actual controlled remediation, independent verification, public open-source repository readiness, and a reproducible demo.

## Additional Constraints

The implementation must demonstrate production-quality engineering while respecting the time constraints of a Google Cloud hackathon.

## Development Workflow

Development strictly adheres to the principles outlined above. All specifications, plans, tasks, and implementations must be governed by this constitution.

## Governance

This constitution supersedes all other practices. All PRs, code reviews, and architecture decisions must verify compliance with these principles. Amendments require documentation and explicit justification.

**Version**: 2.0.0 | **Ratified**: 2026-09-06 | **Last Amended**: 2026-09-08
