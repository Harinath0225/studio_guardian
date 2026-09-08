# Studio Guardian: Flagship Demonstration Guide

Autonomous reliability and revenue-protection system for live media broadcasting.
Demonstrates both **Proactive Predictive Defense** and **Closed-Loop Reactive Fallback**.

---

## 3-Minute Live Demonstration Walkthrough

### Part 1: Proactive Predictive Defense (Predict &rarr; Prevent &rarr; Prove)
1. Navigate to **Tab 1: PREDICT (Risk & Telemetry)**.
2. Note the initial nominal baseline: GPU at 65%, Transcoder latency at 220ms, Queue depth at 6 frames, Error rate nominal at 0.41%.
3. Switch to **Tab 4: GAME DAY (Black Swan Chaos)** and click **Inject Transcoder Surge**.
4. Return to **PREDICT**:
   - Transcoder GPU climbs to 93.4% and Queue depth expands to 48 frames.
   - Composite risk score elevates to **IMMINENT_RISK (0.87)**.
   - Failure horizon countdown computes a failure window between **3 and 8 minutes**.
   - Note that playback error rate remains nominal (0.48%) &mdash; predicting failure *before* audience impact.
5. Click **Data Provenance** in the top right:
   - Inspect the exact raw values, SLO min-max bounds, and feature weights.
6. Switch to **Tab 2: PROTECT (Policy & Scaling)**:
   - Review the candidate action: `scale_transcoder_pool` (8 &rarr; 16 nodes).
   - Review counterfactual ROI: **Estimated Exposure Avoided: $45,660.00**.
   - Safety Director verifies blast radius is 0.0% and marks policy as **Auto-Execute Approved**.
   - Click **Execute Capacity Scaling** (or watch autonomous trigger).
   - Inspect the **Verification Results Panel**: fresh Grafana telemetry confirms GPU drops to 61.2% and queue drops to 12. Verdict: `PREVENTION_VERIFIED`.

---

### Part 2: Semantic Media Quality & Ad Integrity
1. Navigate to **Tab 4: GAME DAY (Black Swan Chaos)**.
2. Click **Inject SCTE-35 Corruption**.
3. Note that server infrastructure (CPU/Memory/GPU) remains nominal (proving the Semantic Media Quality principle).
4. The **Ad Integrity Sentinel** detects:
   - SCTE-35 cue drift of **+420.0ms**, exceeding the configured operational tolerance of &plusmn;200ms.
   - Ad pod drop rises to 8.5%, creating immediate ad revenue exposure.
   - Recommends activating the emergency backup ad slate.

---

### Part 3: Reactive Incident Fallback
1. In **Tab 4: GAME DAY**, click **Inject Sudden Outage**.
2. The UI instantly detects playback error spike (8.7%) in Australia & Singapore and automatically transitions to **Tab 3: RESPOND (Incident Fallback)**.
3. Incident Commander activates:
   - Root Cause Hypothesis identifies transcoder cluster degradation.
   - Business Impact Agent calculates affected viewers (1,820,000) and SLA penalty exposure.
   - Click **Divert 100% Traffic to Standby (transcoder-us-01)**.
   - Fresh telemetry confirms error rate recovers to 0.38% and stream returns to nominal health.

---

### Part 4: Reset
- In the floating bottom simulator bar or Game Day tab, click **Reset Baseline** to instantly return all telemetry to clean nominal state.