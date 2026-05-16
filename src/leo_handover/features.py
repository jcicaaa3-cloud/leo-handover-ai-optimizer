from __future__ import annotations

import pandas as pd

FEATURE_COLUMNS = [
    "elevation_deg",
    "distance_km",
    "rsrp_dbm",
    "link_margin_db",
    "sat_load",
    "remaining_visible_s",
    "relative_velocity_km_s",
    "is_current_sat",
    "handover_penalty",
    "candidate_rank_signal",
    "demand_mbps",
    "time_sin",
    "time_cos",
]

TARGET_COLUMN = "selected"
GROUP_COLUMNS = ["user_id", "timestep"]


def validate_candidate_frame(frame: pd.DataFrame, require_target: bool = True) -> None:
    required = set(FEATURE_COLUMNS + GROUP_COLUMNS + ["sat_id"])
    if require_target:
        required.add(TARGET_COLUMN)
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if require_target and frame[TARGET_COLUMN].isin([0, 1]).all() is False:
        raise ValueError("Target column must be binary 0/1")


def build_xy(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    validate_candidate_frame(frame, require_target=True)
    return frame[FEATURE_COLUMNS].copy(), frame[TARGET_COLUMN].astype(int).copy()


def candidate_feature_dicts(frame: pd.DataFrame) -> list[dict[str, float | int]]:
    """Serialize a candidate frame into API-friendly dictionaries."""

    validate_candidate_frame(frame, require_target=False)
    columns = ["sat_id"] + FEATURE_COLUMNS
    return frame[columns].to_dict(orient="records")
