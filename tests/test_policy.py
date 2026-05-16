from leo_handover.config import SimulationConfig
from leo_handover.evaluation import evaluate_policies
from leo_handover.models import train_handover_model
from leo_handover.simulator import simulate_candidate_dataset


def test_policy_evaluation_returns_expected_metrics():
    cfg = SimulationConfig(n_users=3, n_satellites=28, n_steps=18, seed=11, min_elevation_deg=-8.0)
    frame = simulate_candidate_dataset(cfg)
    bundle = train_handover_model(frame, random_state=11, test_fraction=0.3)
    metrics = evaluate_policies(frame, model_bundle=bundle)
    assert "max_signal" in metrics
    assert "visibility_guard" in metrics
    assert "stability_aware" in metrics
    assert "ai_ranker" in metrics
    assert metrics["ai_ranker"]["decision_epochs"] > 0
    assert 0.0 <= metrics["ai_ranker"]["selection_accuracy"] <= 1.0
    assert "mean_oracle_regret" in metrics["ai_ranker"]
