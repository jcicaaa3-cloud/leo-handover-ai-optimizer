from leo_handover.config import SimulationConfig
from leo_handover.explainability import explain_epoch
from leo_handover.simulator import simulate_candidate_dataset


def test_explain_epoch_returns_ranked_candidates_and_notice():
    cfg = SimulationConfig(n_users=2, n_satellites=24, n_steps=10, seed=17, min_elevation_deg=-8.0)
    frame = simulate_candidate_dataset(cfg)
    explanation = explain_epoch(frame)
    assert explanation["selected_sat_id"] is not None
    assert explanation["ranked_candidates"]
    assert "Synthetic demo" in explanation["notice"]
