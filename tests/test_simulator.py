from leo_handover.config import SimulationConfig
from leo_handover.simulator import simulate_candidate_dataset, summarize_dataset


def test_simulator_generates_labeled_candidate_groups():
    cfg = SimulationConfig(n_users=3, n_satellites=24, n_steps=12, seed=7, min_elevation_deg=-5.0)
    frame = simulate_candidate_dataset(cfg)
    summary = summarize_dataset(frame)
    assert summary["rows"] > 0
    assert summary["positive_labels"] == summary["decision_epochs"]
    positives_per_group = frame.groupby(["user_id", "timestep"])["selected"].sum()
    assert positives_per_group.min() == 1
    assert positives_per_group.max() == 1
