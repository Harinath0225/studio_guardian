<!--
Sync Impact Report:
- Version bump: 0.0.0 -> 1.0.0
- Modified principles: Replaced template placeholders with 20 explicit STUDIO GUARDIAN principles.
- Added sections: Added 20 principles under Core Principles. 
- Removed sections: None.
- Follow-up TODOs: None.
-->

# STUDIO GUARDIAN Constitution

## Core Principles

### 1. Real Agentic System
The product must be a genuine multi-agent system. The architecture must contain distinct specialist agents with explicit responsibilities (Incident Commander, Observability Investigator, Business Impact Agent, Remediation Agent, Verification Agent). Do not simulate multiple agents with prompt labels inside one monolithic LLM call. The Incident Commander is the supervisor and controls workflow progression.

### 2. Hierarchical Supervisor Pattern
Use: Incident Commander → Specialist agents → Shared persistent state → Verification → Loop or resolution. Avoid unnecessary peer-to-peer agent complexity. Agent responsibilities must remain clearly separated.

### 3. Gemini is a Reasoning Component
Gemini must perform meaningful reasoning including evidence correlation, root-cause hypothesis generation, remediation comparison, natural-language explanation, and report generation. Deterministic business logic must remain in code. Gemini must NOT be responsible for authorization, safety enforcement, financial calculations, workflow state transitions, permission checks, or arbitrary infrastructure access.

### 4. Google Cloud is Part of the Real Runtime
The application must genuinely use Google's agent infrastructure and Gemini. Do not build a generic FastAPI application that happens to call Gemini. The Google Cloud agent framework must participate in the agent workflow. The deployed application must demonstrate actual Google Cloud runtime usage.

### 5. Grafana is a First-Class Partner Integration
Grafana must be used at runtime (Hackathon track: Grafana Labs). The project must demonstrate actual use of Grafana MCP. Grafana must provide operational evidence including appropriate combinations of metrics, logs, traces, alerts, dashboards, and incidents. Do not merely include a Grafana logo, screenshots, or README references.

### 6. Media & Entertainment First
This is NOT a generic AIOps product. Every important user-facing concept must relate to live media and entertainment. The primary scenario is a high-profile live entertainment event experiencing a streaming infrastructure failure. The system must reason about viewers, playback quality, transcoding, streaming, geography, advertising windows, subscriber impact, and business exposure.

### 7. Closed-Loop Autonomy
The core product lifecycle is: OBSERVE → INVESTIGATE → CORRELATE → ASSESS → DECIDE → GOVERN → ACT → VERIFY → RESOLVE. The system must not stop at diagnosis.

### 8. Actual Remediation
The Remediation Agent must perform an actual controlled operation in the demo environment (e.g., traffic shift, service scale, controlled restart, configuration change). Changing a database record or UI label alone does not qualify as remediation.

### 9. Independent Verification
The Verification Agent must independently query telemetry after remediation. HTTP success is NOT proof of recovery. The incident can only become RESOLVED when verification confirms recovery.

### 10. Safety By Design
No AI agent receives unrestricted infrastructure access. All remediation passes through a deterministic Safety Director. The policy must evaluate action type, confidence, blast radius, risk, and authorization. Unsafe actions require human approval.

### 11. Persistent System of Record
PostgreSQL is the durable workflow state. Important information must not exist only in React state or process memory. Persist incidents, agent runs, state transitions, observations, hypotheses, business impact, remediation actions, verification, audit events, and incident fingerprints.

### 12. Explainability Without Chain-Of-Thought
Never expose private model chain-of-thought. The product must show concise evidence-based explanations (e.g., "Three correlated signals indicate transcoder-v42 as the most likely source"). Show evidence, confidence, decisions, supporting signals, and actions. Do not display hidden reasoning traces.

### 13. Enterprise Security
Follow least privilege. Never place API keys, service credentials, or infrastructure credentials in the frontend. Use backend-mediated tool access. Production secrets should be compatible with Google Secret Manager.

### 14. UI/UX Quality
The product must look like a premium enterprise product. The visual direction must be modern, sleek, professional, cinematic, highly readable, operational, and user friendly. Use tasteful 3D visual elements where they improve understanding. Avoid gimmicky 3D. The visual language should resemble a futuristic global broadcast operations center.

### 15. Functionality Over Complexity
Prefer one deployable backend over many microservices. Prefer logical agent separation over network-level agent fragmentation. Avoid unnecessary Kubernetes, event infrastructure, vector databases, and distributed systems.

### 16. Demo-First Engineering
The primary demo must work deterministically. The system must support: TRIGGER INCIDENT → RUN MULTI-AGENT WORKFLOW → REMEDIATE → VERIFY → RESOLVE. A judge must be able to reproduce the workflow.

### 17. Hackathon Compliance
The project must satisfy the hackathon requirements for: Gemini, Google Cloud Agent Builder/Platform/ADK, Grafana partner integration, real media and entertainment workflow, public source repository, open-source license, hosted application, reproducible demo, and three-minute functioning demo. The code repository must demonstrate actual runtime partner and Google Cloud usage.

### 18. Testability
Every important capability must be testable. Use automated tests for safety policies, workflow transitions, business impact, agent schemas, remediation, verification, and API behavior.

### 19. Observability Of The Agents
The system itself must be observable. Record agent, run, state, tool invocation, duration, result, failure, and decision. The React UI should expose an understandable operational timeline.

### 20. Winner-Level Product Principle
The product must not feel like "ChatGPT for Grafana". It must feel like: "An autonomous Incident Director purpose-built for live media operations." Every architecture and UX decision should strengthen that story.

## Additional Constraints

The implementation must demonstrate production-quality engineering while respecting the time constraints of a Google Cloud hackathon.

## Development Workflow

Development strictly adheres to the principles outlined above. All specifications, plans, tasks, and implementations must be governed by this constitution.

## Governance

This constitution supersedes all other practices. All PRs, code reviews, and architecture decisions must verify compliance with these principles. Amendments require documentation and explicit justification.

**Version**: 1.0.0 | **Ratified**: 2026-09-06 | **Last Amended**: 2026-09-06
