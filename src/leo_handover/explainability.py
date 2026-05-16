from __future__ import annotations

from typing import Any

import pandas as pd

from .evaluation import _load_aware_score
from .features import validate_candidate_frame
from .models import predict_candidate_scores


def _candidate_reason(row: pd.Series) -> list[str]:
    reasons: list[str] = []
    if row["remaining_visible_s"] >= 240:
        reasons.append("long remaining visibility window")
    elif row["remaining_visible_s"] <= 60:
        reasons.append("short remaining visibility window")

    if row["sat_load"] <= 0.35:
        reasons.append("low satellite load")
    elif row["sat_load"] >= 0.75:
        reasons.append("high satellite load")

    if row["link_margin_db"] >= 20:
        reasons.append("strong link margin")
    elif row["link_margin_db"] < 8:
        reasons.append("thin link margin")

    if row.get("is_current_sat", 0) == 1:
        reasons.append("keeps current connection")
    elif row.get("handover_penalty", 0) == 1:
        reasons.append("requires handover")

    return reasons[:3] or ["balanced score across signal, load, and visibility"]


def explain_epoch(
    frame: pd.DataFrame,
    model_bundle: dict[str, Any] | None = None,
    user_id: int | None = None,
    timestep: int | None = None,
) -> dict[str, Any]:
    """Return a small, human-readable explanation for one decision epoch."""

    validate_candidate_frame(frame, require_target="selected" in frame.columns)
    work = frame.copy()
    if user_id is not None:
        work = work[work["user_id"] == user_id]
    if timestep is not None:
        work = work[work["timestep"] == timestep]
    if work.empty:
        raise ValueError("No candidate rows matched the requested user_id/timestep")

    # Use the first complete epoch if multiple are provided.
    first_key = work[["user_id", "timestep"]].drop_duplicates().iloc[0]
    epoch = work[(work["user_id"] == first_key["user_id"]) & (work["timestep"] == first_key["timestep"])].copy()

    if model_bundle is not None:
        epoch["model_score"] = predict_candidate_scores(model_bundle, epoch)
        score_column = "model_score"
        policy = "ai_ranker"
    else:
        epoch["model_score"] = _load_aware_score(epoch)
        score_column = "model_score"
        policy = "transparent_load_aware_fallback"

    epoch["heuristic_score"] = _load_aware_score(epoch)
    ranked = epoch.sort_values(score_column, ascending=False).reset_index(drop=True)
    selected = ranked.iloc[0]
    runner_up = ranked.iloc[1] if len(ranked) > 1 else None

    margin_to_runner_up = None
    if runner_up is not None:
        margin_to_runner_up = float(selected[score_column] - runner_up[score_column])

    return {
        "policy": policy,
        "user_id": int(selected["user_id"]),
        "timestep": int(selected["timestep"]),
        "selected_sat_id": int(selected["sat_id"]),
        "score_column": score_column,
        "score_margin_to_runner_up": margin_to_runner_up,
        "top_reasons": _candidate_reason(selected),
        "ranked_candidates": [
            {
                "rank": int(rank),
                "sat_id": int(row["sat_id"]),
                "score": float(row[score_column]),
                "link_margin_db": float(row["link_margin_db"]),
                "remaining_visible_s": float(row["remaining_visible_s"]),
                "sat_load": float(row["sat_load"]),
                "notes": _candidate_reason(row),
            }
            for rank, (_, row) in enumerate(ranked.head(5).iterrows(), start=1)
        ],
        "notice": "Synthetic demo data only. Not validated for real satellite-network operations.",
    }
