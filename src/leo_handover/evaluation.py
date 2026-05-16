from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .features import validate_candidate_frame
from .models import predict_candidate_scores

GROUP_KEYS = ["user_id", "timestep"]


def _normalized(series: pd.Series) -> pd.Series:
    lo = float(series.min())
    hi = float(series.max())
    if hi - lo < 1e-9:
        return pd.Series(np.zeros(len(series)), index=series.index)
    return (series - lo) / (hi - lo)


def _load_aware_score(group: pd.DataFrame) -> pd.Series:
    """Transparent heuristic used both as a baseline and as an API fallback."""

    return (
        1.10 * _normalized(group["link_margin_db"])
        + 0.95 * _normalized(group["remaining_visible_s"])
        + 0.35 * _normalized(group["elevation_deg"])
        - 0.85 * group["sat_load"]
        - 0.30 * group["handover_penalty"]
    )


def _stability_aware_score(group: pd.DataFrame) -> pd.Series:
    """Baseline that prefers fewer unnecessary handovers when the current link is healthy."""

    return (
        _load_aware_score(group)
        + 0.38 * group["is_current_sat"]
        - 0.22 * group["handover_penalty"]
        + 0.20 * _normalized(group["remaining_visible_s"])
    )


def _choose_visibility_guard(group: pd.DataFrame) -> int:
    """Pick a candidate with enough remaining visibility, then maximize link margin.

    This is intentionally simple and explainable: it shows why max-signal alone
    is fragile when the strongest satellite is about to leave the user's view.
    """

    enough_time = group[group["remaining_visible_s"] >= 120.0]
    pool = enough_time if not enough_time.empty else group
    return int(pool["link_margin_db"].idxmax())


def choose_policy_indices(
    frame: pd.DataFrame,
    policy: str,
    model_bundle: dict[str, Any] | None = None,
) -> pd.Index:
    validate_candidate_frame(frame, require_target=True)
    frame = frame.copy()
    chosen_indices: list[int] = []

    if policy == "ai_ranker":
        if model_bundle is None:
            raise ValueError("ai_ranker policy requires a trained model bundle")
        frame["policy_score"] = predict_candidate_scores(model_bundle, frame)
        return frame.groupby(GROUP_KEYS)["policy_score"].idxmax()

    for _, group in frame.groupby(GROUP_KEYS, sort=False):
        if policy == "max_signal":
            chosen_indices.append(int(group["rsrp_dbm"].idxmax()))
        elif policy == "sticky_signal":
            sticky = group[
                (group["is_current_sat"] == 1)
                & (group["link_margin_db"] > 7.5)
                & (group["remaining_visible_s"] > 60.0)
            ]
            if not sticky.empty:
                chosen_indices.append(int(sticky["link_margin_db"].idxmax()))
            else:
                chosen_indices.append(int(group["rsrp_dbm"].idxmax()))
        elif policy == "visibility_guard":
            chosen_indices.append(_choose_visibility_guard(group))
        elif policy == "load_aware":
            scores = _load_aware_score(group)
            chosen_indices.append(int(scores.idxmax()))
        elif policy == "stability_aware":
            scores = _stability_aware_score(group)
            chosen_indices.append(int(scores.idxmax()))
        else:
            raise ValueError(f"Unknown policy: {policy}")
    return pd.Index(chosen_indices)


def _oracle_regret(frame: pd.DataFrame, chosen: pd.DataFrame) -> float:
    if "oracle_score" not in frame.columns:
        return 0.0
    best = frame.groupby(GROUP_KEYS)["oracle_score"].max().rename("oracle_best_score")
    merged = chosen.join(best, on=GROUP_KEYS)
    regret = (merged["oracle_best_score"] - merged["oracle_score"]).clip(lower=0.0)
    return float(regret.mean())


def policy_metrics(frame: pd.DataFrame, chosen_indices: pd.Index) -> dict[str, float | int]:
    chosen = frame.loc[chosen_indices].copy().sort_values(GROUP_KEYS)
    handovers = 0
    possible_transitions = 0
    for _, user_choices in chosen.groupby("user_id", sort=False):
        sats = user_choices["sat_id"].to_numpy()
        if len(sats) > 1:
            handovers += int(np.sum(sats[1:] != sats[:-1]))
            possible_transitions += len(sats) - 1

    outage_risk = float((chosen["remaining_visible_s"] <= 60.0).mean())
    return {
        "decision_epochs": int(len(chosen)),
        "selection_accuracy": float(chosen["selected"].mean()),
        "handover_count": int(handovers),
        "handover_rate": float(handovers / max(possible_transitions, 1)),
        "mean_rsrp_dbm": float(chosen["rsrp_dbm"].mean()),
        "mean_link_margin_db": float(chosen["link_margin_db"].mean()),
        "low_margin_rate": float((chosen["link_margin_db"] < 8.0).mean()),
        "mean_sat_load": float(chosen["sat_load"].mean()),
        "mean_remaining_visible_s": float(chosen["remaining_visible_s"].mean()),
        "median_remaining_visible_s": float(chosen["remaining_visible_s"].median()),
        "outage_risk_rate": outage_risk,
        "mean_oracle_regret": _oracle_regret(frame, chosen),
    }


def evaluate_policies(
    frame: pd.DataFrame,
    model_bundle: dict[str, Any] | None = None,
) -> dict[str, dict[str, float | int]]:
    policies = ["max_signal", "sticky_signal", "visibility_guard", "load_aware", "stability_aware"]
    if model_bundle is not None:
        policies.append("ai_ranker")

    results: dict[str, dict[str, float | int]] = {}
    for policy in policies:
        chosen_indices = choose_policy_indices(frame, policy, model_bundle=model_bundle)
        results[policy] = policy_metrics(frame, chosen_indices)
    return results


def filter_holdout_from_bundle(frame: pd.DataFrame, model_bundle: dict[str, Any] | None) -> pd.DataFrame:
    if model_bundle is None:
        return frame
    test_min = model_bundle.get("metadata", {}).get("test_timestep_min")
    if test_min is None:
        return frame
    holdout = frame[frame["timestep"] >= int(test_min)].copy()
    return holdout if not holdout.empty else frame
