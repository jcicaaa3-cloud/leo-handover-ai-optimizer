#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="${PYTHONPATH:-}:src"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}"
python scripts/01_generate_dataset.py --output data/leo_candidates.csv
python scripts/02_train_model.py --input data/leo_candidates.csv --model artifacts/handover_model.joblib --metrics artifacts/training_metrics.json
python scripts/03_evaluate_policy.py --input data/leo_candidates.csv --model artifacts/handover_model.joblib --output docs/evaluation_metrics_example.json
python scripts/05_explain_epoch.py --input data/leo_candidates.csv --model artifacts/handover_model.joblib --output artifacts/epoch_explanation.json
python scripts/04_make_visuals.py --data data/leo_candidates.csv --model artifacts/handover_model.joblib --metrics docs/evaluation_metrics_example.json
python scripts/06_make_report.py --metrics docs/evaluation_metrics_example.json --training artifacts/training_metrics.json --output docs/RUN_REPORT.md
python -m pytest -q
