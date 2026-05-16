# Run Report - LEO Satellite Handover AI Optimizer

> ⚠️ **Synthetic demo only.** This report is generated from a toy LEO simulation. It does not use real satellite operator logs, customer data, commercial network telemetry, or production validation results.

Generated at: `2026-05-16 14:28 UTC`

## Training snapshot

- Train rows: `1251`
- Test rows: `405`
- Temporal holdout starts at timestep: `75`
- Validation top-1 decision accuracy: `0.961864406779661`

## Policy comparison

| Policy | Oracle top-1 | Handover rate | Mean remaining visibility | Low-margin rate | Outage-risk proxy | Oracle regret |
|---|---:|---:|---:|---:|---:|---:|
| max_signal | 0.941 | 0.089 | 259.2s | 0.682 | 0.153 | 0.077 |
| sticky_signal | 0.932 | 0.089 | 257.8s | 0.682 | 0.153 | 0.088 |
| visibility_guard | 0.958 | 0.089 | 265.3s | 0.682 | 0.140 | 0.056 |
| load_aware | 0.962 | 0.089 | 262.6s | 0.682 | 0.153 | 0.029 |
| stability_aware | 0.962 | 0.089 | 265.0s | 0.682 | 0.144 | 0.022 |
| ai_ranker | 0.962 | 0.089 | 263.0s | 0.682 | 0.148 | 0.036 |

## Reading the numbers

The metric to focus on is not just oracle top-1 match. For handover problems, a candidate can look good for one instant but become bad if remaining visibility is short or if the satellite is already heavily loaded. I added handover rate, low-margin rate, outage-risk proxy, and oracle-regret proxy to make those trade-offs visible.

## What this run does **not** prove

This run does not prove production readiness. A real deployment would need a high-fidelity orbit propagator, measured channel behavior, gateway/backhaul constraints, safety guards, monitoring, and validation against real operations data.
