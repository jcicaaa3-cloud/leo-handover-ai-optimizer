from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class SimulationConfig:
    """Configuration for the public, reproducible LEO handover simulator.

    The simulator is intentionally lightweight. It is not a replacement for a
    high-fidelity orbital/network simulator, but it gives a realistic enough
    changing candidate-link table for portfolio experimentation.
    """

    n_users: int = 12
    n_satellites: int = 48
    n_steps: int = 100
    step_seconds: int = 30
    seed: int = 42

    earth_radius_km: float = 6371.0
    orbit_altitude_km: float = 550.0
    inclination_deg: float = 53.0
    gravitational_mu_km3_s2: float = 398600.4418
    earth_rotation_rad_s: float = 7.2921159e-5

    min_elevation_deg: float = 5.0
    max_candidates_per_user: int = 6
    visibility_horizon_steps: int = 24

    def to_dict(self) -> dict[str, int | float]:
        return asdict(self)
