# LEO Satellite Handover AI Optimizer

![LEO Satellite Handover AI Optimizer](docs/assets/readme_hero.png)

> ⚠️ **Synthetic demo / portfolio prototype.** This repository uses fake, simulator-generated data only. It does **not** include real satellite operator logs, customer data, commercial telecom telemetry, or production validation results. The model is not deployed in, nor validated for, a real industrial satellite network.

AI-assisted handover decision prototype for **Low Earth Orbit (LEO) satellite networks**. I built this as a portfolio project to show how a fast-changing connectivity problem can be reframed as a candidate-link ranking problem. For each ground user and decision epoch, the system scores visible satellites using signal quality, remaining visibility, satellite load, and handover cost.

## Why I built it this way

A simple max-signal rule is easy to explain, but it is also short-sighted: the strongest satellite at this instant may disappear below the elevation mask soon after. So the project compares signal-only, sticky, visibility-aware, load-aware, stability-aware, and ML-ranked policies under the same synthetic scenario.

## What this project demonstrates

- Synthetic LEO candidate-link simulator with reproducible scenario generation
- Feature engineering for handover ranking: elevation, distance, RSRP-like signal, link margin, load, remaining visibility, relative velocity, and current-link cost
- Transparent oracle utility for supervised labels
- Temporal holdout evaluation instead of random-only splitting
- Baseline policies: `max_signal`, `sticky_signal`, `visibility_guard`, `load_aware`, `stability_aware`
- AI ranker trained with scikit-learn and compared against the baselines
- FastAPI scoring endpoint plus `/explain` endpoint for decision explanations
- Pytest and GitHub Actions test workflow
- GitHub Pages-ready `index.html` portfolio page

## System design

![Architecture](docs/assets/architecture.png)

The simulator creates a decision table where each row is one candidate satellite link. One row per user/timestep is marked as the oracle-selected satellite. The AI model learns to rank candidates within each decision epoch.

## Reproducible example result

The table below is generated from the included synthetic simulator with a temporal holdout split. Values are a smoke-test benchmark for this public demo, **not** a real-world telecom performance claim.

| Policy | Oracle top-1 match | Handover rate | Mean remaining visibility | Outage-risk proxy | Oracle regret |
|---|---:|---:|---:|---:|---:|
| max_signal | 0.941 | 0.089 | 259.2s | 0.153 | 0.077 |
| sticky_signal | 0.932 | 0.089 | 257.8s | 0.153 | 0.088 |
| visibility_guard | 0.958 | 0.089 | 265.3s | 0.140 | 0.056 |
| load_aware | 0.962 | 0.089 | 262.6s | 0.153 | 0.029 |
| stability_aware | 0.962 | 0.089 | 265.0s | 0.144 | 0.022 |
| ai_ranker | 0.962 | 0.089 | 263.0s | 0.148 | 0.036 |

![Evaluation summary](docs/assets/evaluation_summary.png)

![Risk tradeoff](docs/assets/risk_tradeoff.png)

![Scenario timeline](docs/assets/scenario_timeline.png)

![Feature importance](docs/assets/feature_importance.png)

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export PYTHONPATH=src
python scripts/01_generate_dataset.py --output data/leo_candidates.csv
python scripts/02_train_model.py --input data/leo_candidates.csv --model artifacts/handover_model.joblib
python scripts/03_evaluate_policy.py --input data/leo_candidates.csv --model artifacts/handover_model.joblib --output artifacts/evaluation_metrics.json
python scripts/05_explain_epoch.py --input data/leo_candidates.csv --model artifacts/handover_model.joblib --output artifacts/epoch_explanation.json
python -m pytest -q
```

Or run the full pipeline:

```bash
PYTHONPATH=src bash scripts/run_full_pipeline.sh
```

## API demo

Train a model first, then run:

```bash
PYTHONPATH=src uvicorn leo_handover.api:app --reload
```

Score sample candidates:

```bash
curl -X POST http://127.0.0.1:8000/score \
  -H "Content-Type: application/json" \
  --data @demo/demo_request.json
```

Explain the decision:

```bash
curl -X POST http://127.0.0.1:8000/explain \
  -H "Content-Type: application/json" \
  --data @demo/demo_request.json
```

If no model artifact exists yet, the API uses a transparent fallback load-aware scoring rule. The API response also carries a synthetic-data notice.

## Repository layout

```text
.
├── README.md
├── README_KO.md
├── DISCLAIMER.md
├── DATA_NOTICE.md
├── index.html
├── src/leo_handover/          # simulator, features, model, evaluation, API, explanation
├── scripts/                   # reproducible pipeline scripts
├── tests/                     # pytest smoke tests
├── demo/                      # API request and candidate-link sample
├── docs/                      # portfolio docs, run report, data card, visual assets
├── data/.gitkeep              # generated CSVs are ignored
└── artifacts/.gitkeep         # generated model artifacts are ignored
```

## Core modeling idea

```text
score(candidate satellite) = f(signal, geometry, remaining visibility, load, handover cost)
```

The supervised target comes from a transparent oracle utility, making it easier to explain why a candidate was selected. This is a controlled demo setup; real operations would require a verified source of truth.

## Data and limitations

See [DISCLAIMER.md](DISCLAIMER.md), [DATA_NOTICE.md](DATA_NOTICE.md), [docs/DATA_CARD.md](docs/DATA_CARD.md), and [docs/PRODUCTION_GAP_KO.md](docs/PRODUCTION_GAP_KO.md).

A production-grade extension would need TLE/SGP4 propagation, realistic link budgets, beam/gateway constraints, traffic traces, fail-safe policies, latency budgets, monitoring, and validation against operational data.

## Korean README

See [README_KO.md](README_KO.md).
