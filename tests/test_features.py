from leo_handover.config import SimulationConfig
from leo_handover.features import FEATURE_COLUMNS, build_xy, validate_candidate_frame
from leo_handover.simulator import simulate_candidate_dataset


def test_feature_columns_are_present_and_numeric():
    cfg = SimulationConfig(n_users=2, n_satellites=20, n_steps=8, seed=5, min_elevation_deg=-8.0)
    frame = simulate_candidate_dataset(cfg)
    validate_candidate_frame(frame)
    x, y = build_xy(frame)
    assert list(x.columns) == FEATURE_COLUMNS
    assert y.isin([0, 1]).all()
    assert x.notna().all().all()
