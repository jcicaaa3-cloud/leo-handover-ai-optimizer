from __future__ import annotations

import math
from dataclasses import replace
from typing import Iterable

import numpy as np
import pandas as pd

from .config import SimulationConfig
from .orbital_geometry import (
    elevation_and_distance,
    estimate_remaining_visibility_seconds,
    lla_to_ecef,
    orbital_period_seconds,
    satellite_position_ecef,
)
from .oracle import mark_oracle_selection


def generate_ground_users(cfg: SimulationConfig) -> pd.DataFrame:
    """Create deterministic ground users with heterogeneous demand."""

    rng = np.random.default_rng(cfg.seed)
    service_classes = np.array(["iot", "voice", "video", "enterprise"])
    class_probs = np.array([0.25, 0.25, 0.35, 0.15])
    demand_by_class = {"iot": 1.5, "voice": 3.0, "video": 14.0, "enterprise": 22.0}

    rows = []
    for user_id in range(cfg.n_users):
        service_class = str(rng.choice(service_classes, p=class_probs))
        rows.append(
            {
                "user_id": user_id,
                "lat_deg": float(rng.uniform(-55.0, 55.0)),
                "lon_deg": float(rng.uniform(-180.0, 180.0)),
                "service_class": service_class,
                "demand_mbps": demand_by_class[service_class] + float(rng.normal(0.0, 0.8)),
            }
        )
    users = pd.DataFrame(rows)
    users["demand_mbps"] = users["demand_mbps"].clip(lower=0.5)
    return users


def _satellite_load(sat_id: int, timestep: int, cfg: SimulationConfig) -> float:
    seasonal = 0.45 + 0.25 * math.sin(0.10 * timestep + 0.53 * sat_id)
    burst = 0.10 * math.sin(0.39 * timestep + 1.70 * sat_id + cfg.seed)
    return float(np.clip(seasonal + burst, 0.05, 0.95))


def _relative_velocity_km_s(sat_id: int, timestep: int, cfg: SimulationConfig) -> float:
    base = 2.0 * math.pi * (cfg.earth_radius_km + cfg.orbit_altitude_km) / orbital_period_seconds(cfg)
    # Candidate-specific apparent speed variation.
    return float(base + 0.25 * math.sin(0.15 * timestep + sat_id))


def _rsrp_dbm(distance_km: float, elevation_deg: float, sat_id: int, timestep: int, cfg: SimulationConfig) -> float:
    path_component = 20.0 * math.log10(max(distance_km, 1.0))
    elevation_gain = 0.20 * elevation_deg
    deterministic_fading = 1.8 * math.sin(0.21 * timestep + sat_id * 1.13 + cfg.seed)
    return float(-55.0 - path_component + elevation_gain + deterministic_fading)


def _build_candidate_rows(
    user: pd.Series,
    user_ecef: np.ndarray,
    timestep: int,
    current_sat_id: int | None,
    cfg: SimulationConfig,
) -> pd.DataFrame:
    time_s = float(timestep * cfg.step_seconds)
    raw_candidates: list[dict[str, float | int | str]] = []

    for sat_id in range(cfg.n_satellites):
        sat_ecef = satellite_position_ecef(sat_id, time_s, cfg)
        elevation_deg, distance_km = elevation_and_distance(user_ecef, sat_ecef)
        if elevation_deg < cfg.min_elevation_deg:
            continue
        raw_candidates.append(
            {
                "sat_id": sat_id,
                "elevation_deg": elevation_deg,
                "distance_km": distance_km,
            }
        )

    if not raw_candidates:
        return pd.DataFrame()

    # Keep strongest geometric candidates. A terminal does not evaluate every
    # satellite in a large constellation during every decision epoch.
    raw_candidates = sorted(raw_candidates, key=lambda row: row["elevation_deg"], reverse=True)[
        : cfg.max_candidates_per_user
    ]
    visible_ids = {int(row["sat_id"]) for row in raw_candidates}
    current_visible = current_sat_id in visible_ids if current_sat_id is not None else False

    rows = []
    for row in raw_candidates:
        sat_id = int(row["sat_id"])
        elevation_deg = float(row["elevation_deg"])
        distance_km = float(row["distance_km"])
        rsrp_dbm = _rsrp_dbm(distance_km, elevation_deg, sat_id, timestep, cfg)
        link_margin_db = rsrp_dbm - (-120.0)
        remaining_visible_s = estimate_remaining_visibility_seconds(user_ecef, sat_id, time_s, cfg)
        is_current = int(current_sat_id == sat_id)
        handover_penalty = int(current_visible and current_sat_id != sat_id)
        rows.append(
            {
                "decision_epoch": f"u{int(user.user_id)}_t{timestep}",
                "user_id": int(user.user_id),
                "timestep": timestep,
                "time_s": time_s,
                "sat_id": sat_id,
                "current_sat_id": -1 if current_sat_id is None else int(current_sat_id),
                "is_current_sat": is_current,
                "handover_penalty": handover_penalty,
                "lat_deg": float(user.lat_deg),
                "lon_deg": float(user.lon_deg),
                "service_class": str(user.service_class),
                "demand_mbps": float(user.demand_mbps),
                "elevation_deg": elevation_deg,
                "distance_km": distance_km,
                "rsrp_dbm": rsrp_dbm,
                "link_margin_db": link_margin_db,
                "sat_load": _satellite_load(sat_id, timestep, cfg),
                "remaining_visible_s": remaining_visible_s,
                "relative_velocity_km_s": _relative_velocity_km_s(sat_id, timestep, cfg),
                "time_sin": math.sin(2.0 * math.pi * timestep / max(cfg.n_steps, 1)),
                "time_cos": math.cos(2.0 * math.pi * timestep / max(cfg.n_steps, 1)),
            }
        )

    frame = pd.DataFrame(rows)
    frame = frame.sort_values("rsrp_dbm", ascending=False).reset_index(drop=True)
    frame["candidate_rank_signal"] = np.arange(len(frame), dtype=int)
    return mark_oracle_selection(frame)


def simulate_candidate_dataset(cfg: SimulationConfig | None = None) -> pd.DataFrame:
    """Simulate candidate satellite links and oracle handover labels."""

    cfg = cfg or SimulationConfig()
    if cfg.n_users <= 0 or cfg.n_satellites <= 0 or cfg.n_steps <= 0:
        raise ValueError("n_users, n_satellites, and n_steps must be positive")

    users = generate_ground_users(cfg)
    user_ecef = {
        int(row.user_id): lla_to_ecef(float(row.lat_deg), float(row.lon_deg), cfg.earth_radius_km)
        for row in users.itertuples(index=False)
    }
    current_sat_by_user: dict[int, int | None] = {int(user_id): None for user_id in users["user_id"]}
    all_groups: list[pd.DataFrame] = []

    for timestep in range(cfg.n_steps):
        for user in users.itertuples(index=False):
            user_id = int(user.user_id)
            group = _build_candidate_rows(
                pd.Series(user._asdict()),
                user_ecef[user_id],
                timestep,
                current_sat_by_user[user_id],
                cfg,
            )
            if group.empty:
                current_sat_by_user[user_id] = None
                continue
            selected_row = group.loc[group["selected"] == 1].iloc[0]
            current_sat_by_user[user_id] = int(selected_row["sat_id"])
            all_groups.append(group)

    if not all_groups:
        # Retry with a lower elevation mask for very small test constellations.
        if cfg.min_elevation_deg > -10.0:
            return simulate_candidate_dataset(replace(cfg, min_elevation_deg=-10.0))
        raise RuntimeError("No visible candidate links were generated. Increase n_satellites or n_steps.")

    result = pd.concat(all_groups, ignore_index=True)
    result["selected"] = result["selected"].astype(int)
    result["is_current_sat"] = result["is_current_sat"].astype(int)
    result["handover_penalty"] = result["handover_penalty"].astype(int)
    return result


def summarize_dataset(frame: pd.DataFrame) -> dict[str, int | float]:
    groups = frame.groupby(["user_id", "timestep"], sort=False)
    return {
        "rows": int(len(frame)),
        "decision_epochs": int(groups.ngroups),
        "users": int(frame["user_id"].nunique()),
        "satellites_seen": int(frame["sat_id"].nunique()),
        "avg_candidates_per_epoch": float(len(frame) / max(groups.ngroups, 1)),
        "positive_labels": int(frame["selected"].sum()),
    }
