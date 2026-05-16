from __future__ import annotations

import pandas as pd


def oracle_utility(candidate_frame: pd.DataFrame) -> pd.Series:
    """Reference utility used to create supervised labels.

    The utility balances signal quality, remaining visibility, satellite load,
    and optional handover cost. It is deliberately transparent so the project
    can discuss *why* the AI model makes a handover decision.
    """

    required = {
        "elevation_deg",
        "link_margin_db",
        "remaining_visible_s",
        "sat_load",
        "handover_penalty",
        "relative_velocity_km_s",
    }
    missing = required - set(candidate_frame.columns)
    if missing:
        raise ValueError(f"Missing columns for oracle utility: {sorted(missing)}")

    return (
        0.110 * candidate_frame["elevation_deg"]
        + 0.050 * candidate_frame["link_margin_db"]
        + 0.006 * candidate_frame["remaining_visible_s"]
        - 1.600 * candidate_frame["sat_load"]
        - 0.550 * candidate_frame["handover_penalty"]
        - 0.025 * candidate_frame["relative_velocity_km_s"]
    )


def mark_oracle_selection(candidate_frame: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with oracle_score and selected columns."""

    frame = candidate_frame.copy()
    frame["oracle_score"] = oracle_utility(frame)
    frame["selected"] = 0
    if not frame.empty:
        frame.loc[frame["oracle_score"].idxmax(), "selected"] = 1
    return frame
