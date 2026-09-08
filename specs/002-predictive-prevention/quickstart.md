# Quickstart Validation Guide: Predictive Prevention & Proactive Remediation

**Feature**: [`specs/002-predictive-prevention/spec.md`](file:///c:/Coding_learning/studio_guardian/studio_guardian/specs/002-predictive-prevention/spec.md)
**Status**: Ready for Validation

This guide defines the exact automated tests and manual walkthroughs to validate the feature end-to-end.

---

## 1. Automated Test Suite Execution

Run the predictive test suite using the virtual environment:

```powershell
cd c:\Coding_learning\studio_guardian\studio_guardian\backend
.venv\Scripts\python.exe -m pytest tests/unit/test_predictive_engine.py tests/unit/test_predictive_safety.py -v
```

### Coverage Scope:
- `test_feature_normalizer.py`: Verifies SLO clamping (e.g., 50%–95% GPU) and 60-second linear regression slope calculation.
- `test_risk_model.py`: Verifies deterministic weighted scoring ($\sum w_i \cdot s_i$), contributor breakdown matching total score, and time-to-threshold calculation.
- `test_predictive_safety.py`: Validates that actions with blast radius $>20\%$ or confidence $<85\%$ trigger `WAITING_HUMAN_APPROVAL`, while pre-authorized low blast-radius actions trigger `AUTO_EXECUTE`.
- `test_predictive_verification.py`: Confirms that `PREVENTION_VERIFIED` is strictly emitted when post-action telemetry demonstrates $\ge 25\%$ drop in GPU saturation and risk drops below 25.

---

## 2. End-to-End Live Walkthrough (Demo Scenario)

### Step 1: Start Application Stack
Launch both backend and frontend simultaneously:
```powershell
cd c:\Coding_learning\studio_guardian\studio_guardian
.\scripts\start_local.ps1
```
Open **http://localhost:5173** in your browser.

---

### Step 2: Switch to Predictive Operations Mode
1. On the top Command Center bar, locate the **Mode Toggle** (`PREDICTIVE OPERATIONS` vs `REACTIVE INCIDENT DIRECTOR`).
2. Switch to **Predictive Operations**.
3. Verify the **Unified Agent Runtime & Tool Trace Ledger** shows active connection to `Vertex AI Agent Engine (gemini-2.5-flash)` and `Grafana MCP`.

---

### Step 3: Trigger Emerging Load Surge Scenario
Inject the deterministic predictive load sequence:
```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/prediction/demo/scenario" -Method POST -ContentType "application/json" -Body '{"scenario": "transcoder_saturation_surge", "step": 2}' -UseBasicParsing
```
- Observe the **3D Event Graph**: The `transcoder-worker-pool` node transitions from green to pulsing amber (`#f59e0b`).
- The **Risk Gauge** advances to `ELEVATED RISK` (score ~62).
- The **Predicted Failure Window** displays: `Estimated window: 10–14 minutes`.

---

### Step 4: Advance to Critical Saturation
Advance to Step 3:
```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/prediction/demo/scenario" -Method POST -ContentType "application/json" -Body '{"scenario": "transcoder_saturation_surge", "step": 3}' -UseBasicParsing
```
- The 3D transcoder node turns intense red/coral.
- Risk reaches `IMMINENT RISK` (score ~87).
- The **Safety Director** evaluates:
  - Risk: 0.87 ($\ge 0.80$)
  - Confidence: 0.91 ($\ge 0.85$)
  - Blast radius: 15% ($\le 20\%$)
  - Allowlisted: `scale_transcoder_pool` ($\text{True}$)
- Verdict: **AUTO PREVENT** executes autonomously.
- The 3D visual shows capacity expansion particles around the transcoder node.

---

### Step 5: Verify Prevention & Avoided Exposure
The Verification Agent queries fresh Grafana MCP telemetry:
- GPU saturation drops: $93\% \to 61\%$
- Latency drops: $470\text{ms} \to 260\text{ms}$
- Composite risk drops: $87 \to 18$
- Status stamps: **PREVENTION VERIFIED**
- Counterfactual summary displays:
  - **Estimated Viewers Protected**: `1,250,000`
  - **Commercial Exposure Avoided**: `$45,660` ($46,000 projected loss - $340 scale cost).

---

### Step 6: Test Reactive Fallback (Context Inheritance)
Trigger a sudden catastrophic encoder drop while in predictive mode:
```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/demo/incident" -Method POST -ContentType "application/json" -Body '{"scenario": "video_freeze"}' -UseBasicParsing
```
- The UI automatically flips from Predictive to Reactive mode within 500ms.
- Prior telemetry and root-cause evidence are seamlessly transferred into the reactive `INVESTIGATING` timeline card.
