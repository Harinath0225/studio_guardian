# Mathematical Provenance & Counterfactual ROI Model

## Core Philosophy: Deterministic Arithmetic
Studio Guardian strictly enforces Constitution Principle 4 (Mathematically Traceable Data) and Principle 14 (Counterfactual Honesty):
`RAW GRAFANA VALUE -> SLO CLAMPING -> DIMENSIONLESS FEATURE [0,1] -> WEIGHTED SUM -> GEMINI EXPLANATION`

Generative models are strictly prohibited from hallucinating or calculating raw numbers.

## SLO Normalization Baselines
| Metric | Floor (0.0) | Ceiling (1.0) | Unit |
|:---|:---|:---|:---|
| Transcoder GPU Utilization | 50.0% | 95.0% | % |
| Transcoder Latency | 150.0ms | 500.0ms | ms |
| Queue Depth | 5.0 | 50.0 | frames |
| Playback Error Rate | 0.30% | 1.50% | % |
| Active Viewers | 5,000,000 | 15,000,000 | viewers |

## Composite Risk Weights
- **GPU Pressure**: 0.25
- **Queue Growth**: 0.20
- **Latency Pressure**: 0.20
- **Playback Error Growth**: 0.15
- **Audience Concurrency**: 0.10
- **Deployment Recency Risk**: 0.10

## Financial Honesty & Counterfactual ROI
When prevention successfully mitigates risk before viewer impact, savings are strictly labeled as **Estimated Exposure Avoided**:
- `Expected Loss Without Action` = Projected Disrupted Viewers * (Ad Frequency * Window / 1000) * CPM + SLA Risk
- `Cost of Prevention` = Scaled Worker Nodes * Hourly Cost * Duration
- `Estimated Exposure Avoided` = max(0, Expected Loss - Cost of Prevention)