from __future__ import annotations

import math

import numpy as np

from .config import SimulationConfig


def rotation_x(angle_rad: float) -> np.ndarray:
    c, s = math.cos(angle_rad), math.sin(angle_rad)
    return np.array([[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]], dtype=float)


def rotation_z(angle_rad: float) -> np.ndarray:
    c, s = math.cos(angle_rad), math.sin(angle_rad)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]], dtype=float)


def orbital_period_seconds(cfg: SimulationConfig) -> float:
    radius = cfg.earth_radius_km + cfg.orbit_altitude_km
    return 2.0 * math.pi * math.sqrt(radius**3 / cfg.gravitational_mu_km3_s2)


def lla_to_ecef(lat_deg: float, lon_deg: float, radius_km: float) -> np.ndarray:
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    return np.array(
        [
            radius_km * math.cos(lat) * math.cos(lon),
            radius_km * math.cos(lat) * math.sin(lon),
            radius_km * math.sin(lat),
        ],
        dtype=float,
    )


def satellite_position_ecef(sat_id: int, time_s: float, cfg: SimulationConfig) -> np.ndarray:
    """Approximate circular-orbit satellite ECEF position.

    This public version uses a deterministic Walker-like toy constellation.
    It captures fast topology changes without relying on external TLE files.
    """

    orbital_radius = cfg.earth_radius_km + cfg.orbit_altitude_km
    mean_motion = math.sqrt(cfg.gravitational_mu_km3_s2 / orbital_radius**3)

    n_planes = max(1, int(round(math.sqrt(cfg.n_satellites))))
    sats_per_plane = max(1, int(math.ceil(cfg.n_satellites / n_planes)))
    plane = sat_id // sats_per_plane
    slot = sat_id % sats_per_plane

    raan = 2.0 * math.pi * plane / n_planes
    phase = 2.0 * math.pi * slot / sats_per_plane + 0.23 * plane
    theta = mean_motion * time_s + phase

    perifocal = np.array(
        [orbital_radius * math.cos(theta), orbital_radius * math.sin(theta), 0.0],
        dtype=float,
    )
    inclination = math.radians(cfg.inclination_deg)
    eci = rotation_z(raan) @ rotation_x(inclination) @ perifocal

    # Rotate inertial frame into Earth-fixed frame.
    ecef = rotation_z(-cfg.earth_rotation_rad_s * time_s) @ eci
    return ecef


def elevation_and_distance(user_ecef: np.ndarray, sat_ecef: np.ndarray) -> tuple[float, float]:
    los = sat_ecef - user_ecef
    distance_km = float(np.linalg.norm(los))
    if distance_km == 0:
        return -90.0, 0.0
    up = user_ecef / np.linalg.norm(user_ecef)
    sin_elevation = float(np.dot(los / distance_km, up))
    sin_elevation = max(-1.0, min(1.0, sin_elevation))
    elevation_deg = math.degrees(math.asin(sin_elevation))
    return elevation_deg, distance_km


def estimate_remaining_visibility_seconds(
    user_ecef: np.ndarray,
    sat_id: int,
    current_time_s: float,
    cfg: SimulationConfig,
) -> float:
    """Estimate remaining line-of-sight time using look-ahead sampling."""

    remaining = 0.0
    for step in range(1, cfg.visibility_horizon_steps + 1):
        future_time = current_time_s + step * cfg.step_seconds
        sat_ecef = satellite_position_ecef(sat_id, future_time, cfg)
        elevation_deg, _ = elevation_and_distance(user_ecef, sat_ecef)
        if elevation_deg < cfg.min_elevation_deg:
            break
        remaining += cfg.step_seconds
    return remaining
