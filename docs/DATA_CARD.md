# Data Card - Synthetic LEO Handover Demo Dataset

> ⚠️ **Synthetic demo only.** This data is fake/simulated for portfolio demonstration. It is not real satellite-network telemetry and is not evidence of production performance.

## Purpose

The dataset exists so the full project can run in a public GitHub repository without exposing private or regulated data. It lets reviewers reproduce the pipeline from data generation to model training, evaluation, API scoring, and visualization.

## Generation method

`simulate_candidate_dataset()` creates a candidate-link table. Each row is one visible satellite candidate for one user at one timestep. The simulator uses simplified circular-orbit geometry, sampled ground users, deterministic load variation, RSRP-like signal estimates, and a transparent oracle utility.

## Main columns

- `user_id`, `timestep`, `sat_id`: decision context and candidate satellite
- `elevation_deg`, `distance_km`: simplified geometry features
- `rsrp_dbm`, `link_margin_db`: RSRP-like signal features, not a full RF link budget
- `sat_load`: synthetic congestion/load proxy
- `remaining_visible_s`: look-ahead visibility estimate
- `is_current_sat`, `handover_penalty`: continuity features
- `oracle_score`, `selected`: transparent label used for supervised learning

## Privacy and sensitivity

There is no personal data, no customer data, no real satellite operator data, and no production telemetry.

## Known limitations

- No TLE/SGP4 propagation
- No weather, gateway, backhaul, beam-management, or spectrum constraints
- RSRP values are simplified and deterministic
- Labels come from a hand-built oracle, not field operations
- Results are suitable for portfolio discussion, not industrial validation
