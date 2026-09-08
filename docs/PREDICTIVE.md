# Predictive Prevention & Proactive Remediation Engine

Studio Guardian's **Predictive Prevention & Proactive Remediation Engine** implements the **`PREDICT → PREVENT → PROVE`** paradigm for high-stakes live sports and media streaming (e.g. Cricket World Cup Finals).

Instead of waiting for viewer playback errors to manifest before reacting, Studio Guardian evaluates leading saturation indicators (GPU hardware saturation, worker queue depth, segment fetch latencies) to safely avert incidents before viewer disruption occurs.

---

## 1. Mathematical Risk Modeling & Normalization

### 1.1 Min-Max SLO Boundary Normalization
Each raw telemetry signal $x_i$ is mapped to a normalized pressure score $s_i \in [0.0, 1.0]$ using empirical operational Service Level Objective (SLO) thresholds:

$$\text{clamp}(x, \text{floor}, \text{ceil}) = \max(\text{floor}, \min(\text{ceil}, x))$$

$$s_i = \frac{\text{clamp}(x_i, \text{floor}_i, \text{ceil}_i) - \text{floor}_i}{\text{ceil}_i - \text{floor}_i}$$

#### Operational SLO Baselines
| Signal | Floor (Nominal) | Ceiling (Critical) | Signal Weight ($w_i$) |
| :--- | :--- | :--- | :--- |
| **GPU Utilization** (`gpu_pressure`) | 50.0% | 95.0% | 0.25 |
| **Transcoder Queue Depth** (`queue_growth`) | 5 chunks | 50 chunks | 0.20 |
| **Transcoder Latency** (`latency_pressure`) | 150.0 ms | 500.0 ms | 0.20 |
| **Playback Error Rate** (`error_growth`) | 0.30% | 1.50% | 0.15 |
| **Active Viewers** (`viewer_growth`) | 5,000,000 | 15,000,000 | 0.10 |
| **Deployment Risk** (`deployment_risk`) | > 300s ago | 0s (immediate) | 0.10 |

---

### 1.2 Sliding Window Linear Velocity (First Derivative)
To capture rapid surges before static ceilings are breached, the normalizer maintains a 60-second in-memory ring buffer of telemetry observations. The instantaneous growth rate $m$ (units/minute) is computed via Ordinary Least Squares linear regression:

$$m = \frac{\sum_{i=1}^{n} (t_i - \bar{t})(y_i - \bar{y})}{\sum_{i=1}^{n} (t_i - \bar{t})^2}$$

The velocity is normalized against maximum expected slope:
$$s_{\text{velocity}} = \min\left(1.0, \max\left(0.0, \frac{m}{\text{max\_slope\_per\_min}}\right)\right)$$

### 1.3 Acceleration Calculation (Second Derivative)
Acceleration is determined by bisecting the sample history into two halves and calculating the slope differential:
$$a = m_{\text{second\_half}} - m_{\text{first\_half}}$$

If $a > 0$, an acceleration booster of up to $+0.15$ is applied to the queue pressure signal.

---

### 1.4 Composite Risk Score & Compound Saturation Boost
The linear weighted risk score is:
$$R_{\text{linear}} = \sum_{i=1}^{k} w_i \cdot s_i$$

#### Leading Indicator Compound Boost
In live streaming operations, when primary bottleneck indicators (GPU utilization and queue depth) reach critical levels ($\ge 0.85$ and $\ge 0.80$ respectively), failure is mathematically guaranteed even before downstream players observe buffer exhaustion.

Under this condition, the model applies a compound saturation boost:
$$R_{\text{compound}} = 0.40 \cdot s_{\text{gpu}} + 0.35 \cdot s_{\text{queue}} + 0.25 \cdot s_{\text{latency}}$$
$$R = \max(R_{\text{linear}}, R_{\text{compound}})$$

### 1.5 Risk Tiers
| Tier | Score Range | Operational Meaning | Action |
| :--- | :--- | :--- | :--- |
| **HEALTHY** | $[0.00, 0.30)$ | Nominal live stream conditions | Continuous background polling |
| **WATCH** | $[0.30, 0.60)$ | Moderate utilization or viewer accumulation | Heightened monitoring cadence |
| **ELEVATED_RISK** | $[0.60, 0.80)$ | Approaching warning thresholds | Candidate plan synthesis |
| **HIGH_RISK** | $[0.80, 0.90)$ | Saturation imminent; buffer depletion begins | Safety gating evaluation |
| **IMMINENT_RISK** | $[0.90, 1.00]$ | Buffer starvation within 3–8 minutes | Autonomous preventive scale |

---

### 1.6 Time-to-Threshold Estimation
The estimated time (minutes) until critical threshold breach:
$$T = \max\left(1, \min\left(15, \frac{\text{SLO\_ceil} - x_{\text{current}}}{m + 0.5 \cdot a}\right)\right)$$
Reported as an asymmetric uncertainty interval $[T_{\min}, T_{\max}] = [\max(1, T - 2), T + 4]$.

---

### 1.7 Independent Confidence Scoring
Confidence is decoupled from the risk score to prevent false-positive autonomous interventions on noisy or stale telemetry:
$$C = C_{\text{base}} \cdot f_{\text{freshness}} \cdot f_{\text{completeness}} \cdot f_{\text{concordance}}$$
- **Freshness Penalty**: Telemetry older than 10s degrades confidence ($f_{\text{freshness}} = \max(0.4, 1.0 - \frac{\text{age} - 5}{30})$).
- **Completeness**: Ratio of successfully queried signals vs expected signals.
- **Signal Concordance**: Validates that GPU pressure, queue buildup, and latency agree in directional trend.

---

## 2. Grafana MCP Telemetry Integration

### 2.1 Authoritative Metrics (Prometheus)
Studio Guardian queries the Grafana Model Context Protocol (MCP) server for live time-series:
- **GPU Utilization**:
  ```promql
  avg(media_transcode_gpu_utilization_pct{region="ap-south-1"})
  ```
- **Transcoder Queue Depth**:
  ```promql
  avg(media_transcode_queue_depth{service="transcoder"})
  ```
- **Segment Fetch Latency**:
  ```promql
  histogram_quantile(0.95, sum(rate(media_transcode_latency_seconds_bucket[1m])) by (le)) * 1000
  ```
- **Playback Error Rate**:
  ```promql
  sum(rate(media_playback_errors_total[1m])) / sum(rate(media_playback_requests_total[1m])) * 100
  ```

### 2.2 Corroborating Logs (Loki)
```logql
{service="transcoder"} |= "queue" | json | unwrap depth > 40
```

### 2.3 Provider Toggle (`USE_MOCK_GRAFANA_MCP`)
In `.env` or system environment:
- `USE_MOCK_GRAFANA_MCP=true`: Directs calls to `MockGrafanaServer`, producing realistic simulated load curves.
- `USE_MOCK_GRAFANA_MCP=false`: Dispatches live HTTP requests to the configured Grafana MCP endpoint (`GRAFANA_MCP_SERVER_URL` and `GRAFANA_SERVICE_ACCOUNT_TOKEN`).

All observations, query expressions, durations, and status codes are recorded into the `prediction_evidence` relational table.

---

## 3. Vertex AI Agent Engine Integration

### 3.1 Model & Runtime Configuration
- **Model**: `gemini-2.5-flash` via Google GenAI SDK.
- **Role**: Explains the deterministic feature breakdown, generates structured failure hypotheses, and recommends remediation actions without hallucinating telemetry numbers.

### 3.2 Structured Output Schema (`PredictiveHypothesisOutput`)
Gemini generates typed JSON adhering to:
```python
class PredictiveHypothesisOutput(BaseModel):
    failure_mode: str
    failure_hypothesis: str
    reasoning_summary: str
    recommended_action: str
    uncertainty_factors: List[str]
```

### 3.3 Execution Frames & Runtime Tracing
Every agent invocation generates an execution frame tagged with:
- `agent_engine`: `"Vertex AI (gemini-2.5-flash)"`
- `active_agent`: `"PredictiveRiskAgent"`
- `session_id`: Deterministic UUID session token
- `telemetry_source`: `"LIVE_GRAFANA_MCP"` or `"MOCK_GRAFANA_MCP"`

These frames are persisted and surfaced in the Command Center's **Unified Runtime Execution Ledger**.

---

## 4. Deterministic Safety Gating & Governance

### 4.1 Autonomous Execution Criteria
Autonomous execution without human approval is permitted **only** when all four deterministic criteria pass:
1. **Risk Score**: $\text{risk} \ge 0.80$ (HIGH or IMMINENT risk).
2. **Data Confidence**: $\text{confidence} \ge 0.85$.
3. **Blast Radius**: $\text{blast\_radius} \le 20.0\%$.
4. **Action Allowlist**: Action must be allowlisted (`scale_transcoder_pool`).

If any criterion fails (e.g. blast radius $= 25.0\%$ or confidence $= 0.78$), the system transitions to `WAITING_HUMAN_APPROVAL`, locking execution until authorized by an operator.

---

## 5. Prevention Economics & Counterfactual Accounting

### 5.1 Loss vs. Cost Trade-Off Model
- **Expected Loss Without Action**:
  $$\text{Loss} = \text{Viewers At Risk} \times \text{CPM} \times \text{Downtime Minutes} + \text{SLA Penalty}$$
  For example: $1,820,000$ viewers $\times$ \$0.01/min $\approx \$18,000$.
- **Cost of Prevention**:
  $$\text{Cost} = \Delta \text{Workers} \times \text{Instance Cost per Minute} \times \text{Window}$$
  For example: $8 \text{ additional GPUs} \times \$0.95/\text{hr} \approx \$450$.
- **Net Avoided Exposure**:
  $$\text{Net Avoided} = \text{Expected Loss} - \text{Cost of Prevention} = \$18,000 - \$450 = \$17,550$$

---

## 6. Post-Prevention Verification & Memory Indexing

### 6.1 Verification Criteria
Following action execution, the `VerificationAgent` queries Grafana MCP at $t+30\text{s}$ and $t+60\text{s}$ to enforce recovery:
- $\Delta \text{GPU Utilization} \le -25.0\%$
- $\Delta \text{Risk Score} \le -0.50$
- Playback Error Rate remains $\le 0.50\%$

### 6.2 Episodic Memory Fingerprint
Upon successful verification, the incident fingerprint (symptom vector, dominant factors, proven action, and success rate) is indexed into `prediction_fingerprints` and Vertex AI Vector Memory for continuous organizational learning.
