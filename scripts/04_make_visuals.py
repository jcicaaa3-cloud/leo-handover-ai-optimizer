from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from leo_handover.evaluation import filter_holdout_from_bundle
from leo_handover.models import feature_importances, load_model, predict_candidate_scores


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def make_hero(path: Path) -> None:
    _ensure_parent(path)
    fig, ax = plt.subplots(figsize=(12, 4.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4)
    ax.axis("off")
    # Earth arc and ground terminal
    earth = plt.Circle((2.0, -4.7), 6.0, fill=False, linewidth=2)
    ax.add_patch(earth)
    ax.scatter([2.1], [1.0], s=90)
    ax.text(1.15, 0.55, "Ground user", fontsize=11)
    # Satellites and links
    sats = [(4.4, 3.2), (6.2, 2.8), (8.0, 3.4), (9.5, 2.4)]
    for idx, (x, y) in enumerate(sats):
        ax.scatter([x], [y], marker="s", s=90)
        ax.text(x - 0.28, y + 0.28, f"SAT-{idx}", fontsize=9)
        ax.plot([2.1, x], [1.0, y], linestyle="--", linewidth=1)
    ax.annotate("AI handover ranker", xy=(6.2, 2.8), xytext=(6.0, 0.8), arrowprops={"arrowstyle": "->"}, fontsize=14)
    ax.text(0.3, 3.55, "LEO Satellite Handover AI Optimizer", fontsize=20, weight="bold")
    ax.text(0.35, 3.15, "Signal quality + remaining visibility + satellite load + handover cost", fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def make_architecture(path: Path) -> None:
    _ensure_parent(path)
    fig, ax = plt.subplots(figsize=(12, 4.8))
    ax.axis("off")
    boxes = [
        ("LEO toy constellation\n+ ground users", 0.6, 2.4),
        ("Candidate link\nfeature table", 3.0, 2.4),
        ("Oracle utility\nlabeling", 5.4, 2.4),
        ("AI ranker\ntraining", 7.8, 2.4),
        ("Policy evaluation\n+ API scoring", 10.2, 2.4),
    ]
    for text, x, y in boxes:
        rect = plt.Rectangle((x, y), 1.7, 1.0, fill=False, linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x + 0.85, y + 0.5, text, ha="center", va="center", fontsize=10)
    for i in range(len(boxes) - 1):
        x0 = boxes[i][1] + 1.7
        x1 = boxes[i + 1][1]
        ax.annotate("", xy=(x1, 2.9), xytext=(x0, 2.9), arrowprops={"arrowstyle": "->"})
    ax.text(0.6, 1.3, "Output: selected satellite ID, ranked candidates, policy metrics, explanation JSON", fontsize=12)
    ax.text(0.6, 1.05, "Notice: synthetic demo data only; not production validation", fontsize=10)
    ax.set_xlim(0, 12.3)
    ax.set_ylim(1.0, 4.0)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _read_metrics(metrics_path: Path) -> dict:
    raw = json.loads(metrics_path.read_text(encoding="utf-8"))
    return raw.get("metrics", raw)


def make_evaluation(metrics_path: Path, output: Path) -> None:
    _ensure_parent(output)
    metrics = _read_metrics(metrics_path)
    names = list(metrics.keys())
    acc = [metrics[name]["selection_accuracy"] for name in names]
    fig, ax = plt.subplots(figsize=(10.2, 4.8))
    ax.bar(names, acc)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Oracle top-1 match")
    ax.set_title("Policy comparison on temporal holdout")
    ax.tick_params(axis="x", rotation=20)
    for i, value in enumerate(acc):
        ax.text(i, value + 0.02, f"{value:.2f}", ha="center")
    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def make_risk_tradeoff(metrics_path: Path, output: Path) -> None:
    _ensure_parent(output)
    metrics = _read_metrics(metrics_path)
    names = list(metrics.keys())
    x = [metrics[name].get("handover_rate", 0.0) for name in names]
    y = [metrics[name].get("outage_risk_rate", 0.0) for name in names]
    sizes = [80 + 400 * max(metrics[name].get("mean_oracle_regret", 0.0), 0.0) for name in names]
    fig, ax = plt.subplots(figsize=(8.8, 5.0))
    ax.scatter(x, y, s=sizes)
    for name, xx, yy in zip(names, x, y):
        ax.annotate(name, (xx, yy), xytext=(5, 5), textcoords="offset points", fontsize=9)
    ax.set_xlabel("Handover rate")
    ax.set_ylabel("Outage-risk proxy")
    ax.set_title("Policy trade-off: stability vs. outage risk")
    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def make_timeline(data_path: Path, model_path: Path, output: Path) -> None:
    _ensure_parent(output)
    frame = pd.read_csv(data_path)
    bundle = load_model(model_path)
    frame = filter_holdout_from_bundle(frame, bundle)
    first_user = int(frame["user_id"].iloc[0])
    user_frame = frame[frame["user_id"] == first_user].copy()
    user_frame["ai_score"] = predict_candidate_scores(bundle, user_frame)
    ai = user_frame.loc[user_frame.groupby("timestep")["ai_score"].idxmax()].sort_values("timestep")
    oracle = user_frame.loc[user_frame.groupby("timestep")["selected"].idxmax()].sort_values("timestep")
    fig, ax = plt.subplots(figsize=(10, 4.3))
    ax.plot(oracle["timestep"], oracle["sat_id"], marker="o", label="oracle")
    ax.plot(ai["timestep"], ai["sat_id"], marker="x", label="AI ranker")
    ax.set_xlabel("timestep")
    ax.set_ylabel("selected satellite ID")
    ax.set_title(f"Example handover timeline - user {first_user}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def make_feature_importance(model_path: Path, output: Path) -> None:
    _ensure_parent(output)
    bundle = load_model(model_path)
    importance = feature_importances(bundle).head(10).sort_values("importance")
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    ax.barh(importance["feature"], importance["importance"])
    ax.set_xlabel("importance")
    ax.set_title("Top model features")
    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/leo_candidates.csv")
    parser.add_argument("--model", default="artifacts/handover_model.joblib")
    parser.add_argument("--metrics", default="docs/evaluation_metrics_example.json")
    parser.add_argument("--assets", default="docs/assets")
    args = parser.parse_args()

    assets = Path(args.assets)
    make_hero(assets / "readme_hero.png")
    make_architecture(assets / "architecture.png")
    make_evaluation(Path(args.metrics), assets / "evaluation_summary.png")
    make_timeline(Path(args.data), Path(args.model), assets / "scenario_timeline.png")
    make_feature_importance(Path(args.model), assets / "feature_importance.png")
    make_risk_tradeoff(Path(args.metrics), assets / "risk_tradeoff.png")


if __name__ == "__main__":
    main()
