from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .config import SimulationConfig
from .evaluation import evaluate_policies, filter_holdout_from_bundle
from .explainability import explain_epoch
from .models import load_model, save_model, train_handover_model
from .simulator import simulate_candidate_dataset, summarize_dataset

DATA_NOTICE = "Synthetic demo data only. No real satellite/operator/customer data is included."


def _cmd_generate(args: argparse.Namespace) -> None:
    cfg = SimulationConfig(
        n_users=args.n_users,
        n_satellites=args.n_satellites,
        n_steps=args.n_steps,
        seed=args.seed,
        min_elevation_deg=args.min_elevation_deg,
    )
    frame = simulate_candidate_dataset(cfg)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False)
    print(json.dumps({"notice": DATA_NOTICE, "output": str(output), **summarize_dataset(frame)}, indent=2))


def _cmd_train(args: argparse.Namespace) -> None:
    frame = pd.read_csv(args.input)
    bundle = train_handover_model(frame, random_state=args.seed, test_fraction=args.test_fraction)
    bundle["metadata"]["data_notice"] = DATA_NOTICE
    save_model(bundle, args.model)
    metrics_path = Path(args.metrics)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(bundle["metadata"], indent=2), encoding="utf-8")
    print(json.dumps({"notice": DATA_NOTICE, "model": args.model, "metrics": bundle["metadata"]}, indent=2))


def _cmd_evaluate(args: argparse.Namespace) -> None:
    frame = pd.read_csv(args.input)
    bundle = load_model(args.model) if args.model else None
    eval_frame = filter_holdout_from_bundle(frame, bundle) if args.holdout_only else frame
    metrics = evaluate_policies(eval_frame, model_bundle=bundle)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {"notice": DATA_NOTICE, "metrics": metrics} if args.wrap_notice else metrics
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


def _cmd_explain(args: argparse.Namespace) -> None:
    frame = pd.read_csv(args.input)
    bundle = load_model(args.model) if args.model and Path(args.model).exists() else None
    explanation = explain_epoch(frame, model_bundle=bundle, user_id=args.user_id, timestep=args.timestep)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(explanation, indent=2), encoding="utf-8")
    print(json.dumps(explanation, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LEO handover optimization CLI")
    subparsers = parser.add_subparsers(required=True)

    generate = subparsers.add_parser("generate", help="Generate synthetic candidate-link dataset")
    generate.add_argument("--output", default="data/leo_candidates.csv")
    generate.add_argument("--n-users", type=int, default=12)
    generate.add_argument("--n-satellites", type=int, default=48)
    generate.add_argument("--n-steps", type=int, default=100)
    generate.add_argument("--seed", type=int, default=42)
    generate.add_argument("--min-elevation-deg", type=float, default=5.0)
    generate.set_defaults(func=_cmd_generate)

    train = subparsers.add_parser("train", help="Train AI ranker")
    train.add_argument("--input", default="data/leo_candidates.csv")
    train.add_argument("--model", default="artifacts/handover_model.joblib")
    train.add_argument("--metrics", default="artifacts/training_metrics.json")
    train.add_argument("--seed", type=int, default=42)
    train.add_argument("--test-fraction", type=float, default=0.25)
    train.set_defaults(func=_cmd_train)

    evaluate = subparsers.add_parser("evaluate", help="Compare handover policies")
    evaluate.add_argument("--input", default="data/leo_candidates.csv")
    evaluate.add_argument("--model", default="artifacts/handover_model.joblib")
    evaluate.add_argument("--output", default="artifacts/evaluation_metrics.json")
    evaluate.add_argument("--holdout-only", action="store_true", default=True)
    evaluate.add_argument("--wrap-notice", action="store_true", help="Wrap metrics with a synthetic-data notice")
    evaluate.set_defaults(func=_cmd_evaluate)

    explain = subparsers.add_parser("explain", help="Explain one user/timestep handover decision")
    explain.add_argument("--input", default="data/leo_candidates.csv")
    explain.add_argument("--model", default="artifacts/handover_model.joblib")
    explain.add_argument("--user-id", type=int, default=None)
    explain.add_argument("--timestep", type=int, default=None)
    explain.add_argument("--output", default="artifacts/epoch_explanation.json")
    explain.set_defaults(func=_cmd_explain)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
