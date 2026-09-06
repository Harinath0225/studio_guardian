# Studio Guardian — Hackathon Submission Summary

**Google Cloud & Grafana Labs Hackathon**  
**Category**: Live Media & Entertainment Operations / Autonomous SRE

---

## Pitch Elevator

During a major live event like the Cricket World Cup or Super Bowl, every second of streaming buffer costs tens of thousands of dollars in unserved ads, breaches broadcast SLAs, and sparks immediate subscriber churn. 

**Studio Guardian** is an autonomous, multi-agent live media operations director. Powered by **Gemini 2.5 on Google Cloud** and the **Grafana Labs Model Context Protocol (MCP)**, Studio Guardian autonomously detects stream degradation, correlates Prometheus metrics, Loki crash logs, and Tempo distributed traces, evaluates business blast radius, enforces deterministic safety policy, shifts traffic to warm standbys, and independently verifies recovery—all within 90 seconds.

---

## Key Achievements & Deliverables

- **Real Google GenAI SDK & Vertex AI Runtime**: Powered by Gemini 2.5 Flash with strict Pydantic v2 structured output enforcement across 5 specialist agents.
- **Official Grafana MCP Integration**: Real MCP client adapters executing JSON-RPC tool calls for Prometheus metrics, Loki logs, Tempo traces, and Grafana Alerting.
- **Deterministic Safety Director**: Mathematical policy engine enforcing a 25% blast radius limit, 85% diagnostic confidence floor, and strict mutation allowlists.
- **Live Video Proxy Traffic Shifting**: Real operational remediation that shifts ingest traffic on the fly, paired with independent telemetry verification.
- **Cinematic React + Three.js 3D Command Center**: Live interactive spatial broadcast mesh globe, 1 Hz real-time SSE telemetry charts, and automated post-incident Engineering RCA generation.
- **100% Test Coverage**: 41 automated tests across end-to-end happy paths, failure escalations, MCP adapters, safety policies, and schema boundaries.

---

## 3-Minute Demo Video Script Outline

### [0:00 - 0:35] The Problem
- *Visual*: Millions watching a live global sports championship.
- *Narrator*: "During a live final with 12 million viewers, an origin transcode pod crashes after an urgent patch. Playback buffers spike to 8.7%. In traditional operations, engineers spend 15 minutes manually opening dashboards in Grafana, parsing logs, and debating remediation."

### [0:35 - 1:15] Investigation via Grafana MCP
- *Visual*: Studio Guardian Command Center. The 3D broadcast globe turns red. Alert fires.
- *Narrator*: "Studio Guardian's Incident Commander triggers instantly. The Observability Investigator calls Grafana MCP tools—pulling Prometheus buffer metrics, finding segmentation faults in Loki logs, and pinpointing a 4.8s upstream bottleneck in Tempo traces."

### [1:15 - 1:55] Business Impact & Safety Governance
- *Visual*: Business Impact card and Autonomy Dial.
- *Narrator*: "Simultaneously, the Business Impact Agent calculates 1.8M disrupted viewers and $18,750 in unserved ad exposure. The Safety Director evaluates the proposed traffic shift: blast radius is 14.7% (below the 25% safety ceiling) with 92% diagnostic confidence. It issues an autonomous execution authorization."

### [1:55 - 2:35] Remediation & Independent Verification
- *Visual*: Video routing table changes. Standby node turns green.
- *Narrator*: "The Remediation Agent shifts 100% of AU/SG traffic to the warm standby cluster. Crucially, the Verification Agent does not trust the fix blindly—it independently queries Prometheus over a 15-second window, confirming buffer error rates dropped back to 0.38%."

### [2:35 - 3:00] Resolution & Automated RCA
- *Visual*: 3D globe turns emerald green. Status shows RESOLVED. Report Drawer opens.
- *Narrator*: "Stream restored in under 90 seconds without human intervention. Studio Guardian immediately compiles an Engineering RCA report and Executive Brief ready for broadcast directors. That is the future of autonomous live entertainment operations."
