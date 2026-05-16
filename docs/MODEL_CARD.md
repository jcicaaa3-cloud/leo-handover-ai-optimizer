# Model Card - LEO Handover AI Optimizer

> ⚠️ Public portfolio model. Trained on synthetic demo data only. Not validated for real satellite-network operations.

## Intended use

This model ranks candidate LEO satellite links for a ground-terminal handover decision. It is designed as a portfolio-grade research prototype and educational baseline, not as a production network controller.

## Out-of-scope use

- Real-time control of satellite or telecom infrastructure
- Commercial deployment decisions
- Safety-critical network automation
- Claims of real-world handover performance

## Inputs

The model consumes per-candidate features such as elevation angle, distance, RSRP-like signal estimate, link margin, satellite load, remaining visibility time, relative velocity, whether the satellite is currently connected, and a handover penalty indicator.

## Output

For each candidate satellite, the model outputs a score interpreted as the likelihood that the candidate matches the transparent oracle utility. The selected satellite is the highest-scoring candidate within the decision epoch.

## Training data

The public repository uses a reproducible synthetic LEO network simulation. This avoids exposing private telecom logs or proprietary satellite traces while keeping the full ML pipeline runnable.

## Evaluation

Evaluation uses temporal holdout timesteps and compares the AI ranker against multiple heuristics. Metrics include oracle top-1 match, handover rate, outage-risk proxy, low-margin rate, remaining visibility, and oracle-regret proxy.

## Limitations

- Orbital motion is simplified and does not use TLE/SGP4 propagation.
- Wireless channel modeling is approximate and RSRP-like, not a full link budget.
- The supervised label follows a transparent oracle, so real-world validation would require operational traces or a high-fidelity simulator.
- The API is a scoring contract demonstration, not a real-time controller.

## Responsible deployment notes

A production system should include safety guards, fallback policies, monitoring, latency budgets, fairness across user classes, gateway/beam constraints, security review, and validation under realistic mobility, weather, congestion, and gateway conditions.
