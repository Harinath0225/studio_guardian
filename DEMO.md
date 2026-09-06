# Studio Guardian — 3-Minute Judge Reproduction Guide

Follow these exact steps to run and evaluate **Studio Guardian** during hackathon judging.

---

## Prerequisites

- **Python 3.12+** with `uv` or `pip`
- **Node.js 18+** with `npm`
- Git

---

## Option 1: Automated 1-Click Reproduction (Recommended)

In terminal 1, start the backend:
```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

uv pip install -r pyproject.toml
uvicorn src.main:app --port 8000
```

In terminal 2, execute the judge reproduction script:
```bash
python scripts/run_demo.py
```

This runs the entire end-to-end incident lifecycle with real-time logs:
1. Verifies healthy baseline.
2. Triggers the India vs Australia Final transcoding memory segfault.
3. Observability Investigator queries Grafana MCP.
4. Business Impact Agent computes viewer and ad burn figures.
5. Safety Director evaluates the 25% blast radius policy.
6. Remediation Agent executes controlled traffic shifting on the video proxy.
7. Verification Agent confirms stabilization.
8. Automatically fetches and prints the completed Engineering RCA report!

---

## Option 2: Interactive Web UI Experience

### 1. Launch the Backend
```bash
cd backend
uvicorn src.main:app --port 8000 --reload
```

### 2. Launch the Frontend
```bash
cd frontend
npm install
npm run dev
```
Open **http://localhost:5173** in your browser.

---

## Walkthrough Steps for Judges

1. **Observe Nominal State**:
   - The 3D Broadcast Globe in the top-left pulses in **emerald green**.
   - Playback error rate is `< 0.5%`, transcode latency is `~18ms`.
   - All specialist agents in the control room show `IDLE`.

2. **Trigger Degradation**:
   - Click the red **"Trigger Incident"** button on the floating demo bar (or top-right header).
   - Instant state transition: 3D globe turns **red**, error rate spikes to `8.7%`, and Prometheus alert `HighMediaBufferRatioAlert` fires.

3. **Watch Autonomous Multi-Agent Response**:
   - **Observability Investigator**: Active pulse turns cyan; samples Grafana Prometheus, Loki, and Tempo. Correlates SEI segfault with recent deployment.
   - **Business Impact Agent**: Quantifies `1,820,000` disrupted viewers, `72,800` VIP 4K subscribers, and `$18,750` ad revenue exposure.
   - **Safety Director**: Checks policy rules. Blast radius is `14.7%` (&le; 25.0%), confidence is `92%` (&ge; 85%) &rarr; issues `AUTO_EXECUTE`.
   - **Remediation Agent**: Dispatches traffic shift to warm standby `transcoder-us-01`.
   - **Verification Agent**: Independently samples Prometheus metrics; verifies error rate dropped to `0.38%` and latency dropped to `19.5ms`.

4. **Stream Restored (RESOLVED)**:
   - 3D globe transitions back to glowing **emerald green**.
   - Traffic routing dial shifts 100% of AU/SG traffic to standby.
   - Status badge shows `RESOLVED`.

5. **Inspect Post-Incident Reports**:
   - Click **"Open Post-Incident RCA Drawer"** in the footer.
   - View the complete Engineering RCA with before/after telemetry deltas and the Executive Sponsor Brief.
   - Download the generated markdown report directly.

6. **Test Escalation Safeguard (Force Failure)**:
   - Click **"Force Escalate"**.
   - Studio Guardian attempts remediation, detects persistent failure, retries once, and then cleanly transitions to **`ESCALATED_HUMAN_TAKEOVER`** to protect the broadcast.
