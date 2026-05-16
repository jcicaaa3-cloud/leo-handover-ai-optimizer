from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _metric_table(metrics: dict) -> str:
    header = (
        "| Policy | Oracle top-1 | Handover rate | Mean remaining visibility | "
        "Low-margin rate | Outage-risk proxy | Oracle regret |\n"
        "|---|---:|---:|---:|---:|---:|---:|"
    )
    rows = []
    for name, item in metrics.items():
        rows.append(
            "| {name} | {acc:.3f} | {handover:.3f} | {visibility:.1f}s | {low_margin:.3f} | {outage:.3f} | {regret:.3f} |".format(
                name=name,
                acc=item.get("selection_accuracy", 0.0),
                handover=item.get("handover_rate", 0.0),
                visibility=item.get("mean_remaining_visible_s", 0.0),
                low_margin=item.get("low_margin_rate", 0.0),
                outage=item.get("outage_risk_rate", 0.0),
                regret=item.get("mean_oracle_regret", 0.0),
            )
        )
    return "\n".join([header, *rows])


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a short portfolio run report")
    parser.add_argument("--metrics", default="docs/evaluation_metrics_example.json")
    parser.add_argument("--training", default="artifacts/training_metrics.json")
    parser.add_argument("--output", default="docs/RUN_REPORT.md")
    args = parser.parse_args()

    metrics = _load_json(Path(args.metrics))
    training = _load_json(Path(args.training))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    report = f"""# Run Report - LEO Satellite Handover AI Optimizer

> ⚠️ **Synthetic demo only.** This report is generated from a toy LEO simulation. It does not use real satellite operator logs, customer data, commercial network telemetry, or production validation results.

Generated at: `{now}`

## Training snapshot

- Train rows: `{training.get('train_rows', 'n/a')}`
- Test rows: `{training.get('test_rows', 'n/a')}`
- Temporal holdout starts at timestep: `{training.get('test_timestep_min', 'n/a')}`
- Validation top-1 decision accuracy: `{training.get('validation_metrics', {}).get('top1_decision_accuracy', 'n/a')}`

## Policy comparison

{_metric_table(metrics)}

## Reading the numbers

The metric to focus on is not just oracle top-1 match. For handover problems, a candidate can look good for one instant but become bad if remaining visibility is short or if the satellite is already heavily loaded. I added handover rate, low-margin rate, outage-risk proxy, and oracle-regret proxy to make those trade-offs visible.

## What this run does **not** prove

This run does not prove production readiness. A real deployment would need a high-fidelity orbit propagator, measured channel behavior, gateway/backhaul constraints, safety guards, monitoring, and validation against real operations data.
"""
    output.write_text(report, encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
