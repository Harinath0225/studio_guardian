# Quickstart Validation Guide: Predictive Media Protection & Black Swan Defense

**Feature**: Predictive Media Protection & Black Swan Defense  
**Branch**: `003-predictive-defense`  
**Date**: 2026-09-08  

This guide provides end-to-end instructions for running and validating both the **Predictive Defense** lifecycle (Predict → Prevent → Prove) and the **Black Swan Defense** lifecycle (Inject → Detect → Remediate → Verify).

---

## 1. Prerequisites & Environment Setup

1. **Python Virtual Environment**:
   ```bash
   cd backend
   .\.venv\Scripts\activate
   ```
2. **Node Environment**:
   ```bash
   cd frontend
   npm install
   ```
3. **Grafana MCP Server**:
   Ensure the Grafana MCP server or local mock is active:
   ```bash
   # In backend/.env
   GRAFANA_MCP_SERVER_URL=http://localhost:8001
   USE_MOCK_GRAFANA_MCP=true # Set to false if Docker Grafana container is running
   ```

---

## 2. Launching the Application

### 2.1 Start Backend Daemon
```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn src.main:app --port 8000 --reload
```
*Health Check*: `curl http://localhost:8000/api/v1/predictive/status`

### 2.2 Start Frontend Dev Server
```powershell
cd frontend
npm run dev
```
*Access UI*: Open `http://localhost:5173` in a modern browser.

---

## 3. Flagship Demo Scenarios

### Scenario A: Flagship Predictive Defense (Predict → Prevent → Prove)

1. **Observe Baseline Nominal State**:
   - Navigate to the **PREDICT** tab on `http://localhost:5173`.
   - Verify that the operational state reports `HEALTHY` (Risk Score <0.30, GPU ~65%, Error Rate ~0.41%).
   - Verify the 3D topology shows green nominal nodes and calm data pulses.

2. **Inject Transcoder Capacity Surge**:
   - Navigate to the **GAME DAY** tab.
   - Click the **"Inject Transcoder Surge"** button (or call `POST /api/v1/demo/black-swan/inject` with `{"scenario_name": "TRANSCODER_SURGE"}`).
   - Switch back to the **PREDICT** tab.

3. **Verify Predictive Detection**:
   - Confirm Risk Score immediately spikes to `>0.85` (`HIGH_RISK` or `IMMINENT_RISK`).
   - Confirm the failure horizon estimates **3–7 minutes** until player-side playback failure.
   - Confirm the top signal contributor is **GPU Saturation (93.4%)** followed by **Queue Buildup (48 chunks)**.
   - Click the GPU metric number to open the **Data Provenance Drawer** and inspect the raw MCP PromQL query and normalization formula.

4. **Verify Governance & Autonomous Prevention**:
   - Switch to the **PROTECT** tab.
   - Inspect the **Safety Director** panel: confirm `AUTO_EXECUTE` policy verdict (Risk ≥0.80, Confidence ≥0.85, Blast Radius ≤20%).
   - Inspect the **Counterfactual ROI**: confirm "Estimated Exposure Avoided: ~$47,820" (explicitly marked `ESTIMATED`).
   - Click **"Execute Transcoder Scale"** (or observe autonomous execution).

5. **Verify Stabilization & Proof**:
   - The system re-queries Grafana MCP post-stabilization (5 seconds).
   - Observe GPU drop from 93.4% to ~61%, queue depth drop to ~12.
   - Status transitions to **"PREDICTED RISK MITIGATED"**.
   - Review the closed-loop evidentiary audit in the Technical Evidence Panel.

---

### Scenario B: Semantic Ad Integrity & SCTE-35 Corruption

1. **Inject SCTE-35 Corruption**:
   - From the **GAME DAY** tab, click **"Inject SCTE-35 Corruption"**.
   - Note that CPU, GPU, and HTTP server health remain 100% green.

2. **Inspect Semantic Detection**:
   - Observe the **Ad Integrity Sentinel** warning badge activate.
   - SCTE timing drift indicates **>350ms** (exceeding configured operational tolerance of ±200ms).
   - Ad revenue burn rate calculation indicates estimated lost revenue at $28.50 CPM.

3. **Trigger Secondary Path / Backup Slate**:
   - In the **PROTECT** view, observe the recommended action: `switch_packager_backup` or `activate_ad_slate`.
   - Execute the action and verify SCTE timing realigns to nominal (<20ms).

---

## 4. Automated Verification Suite

Run the full automated test suite to validate mathematics, policy, agents, and mock Grafana MCP:
```powershell
cd backend
.\.venv\Scripts\pytest tests/ -v
```

Expected Outcome: All unit, integration, and e2e test cases pass with zero failures.
