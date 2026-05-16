import leo_handover.api as api
from leo_handover.api import Candidate, ScoreRequest, score


def test_api_scores_candidates_and_returns_synthetic_notice(monkeypatch):
    monkeypatch.setenv("LEO_HANDOVER_MODEL", "artifacts/__missing_test_model__.joblib")
    api._MODEL_BUNDLE = None
    request = ScoreRequest(
        user_id=1,
        timestep=3,
        candidates=[
            Candidate(
                sat_id=10,
                elevation_deg=30,
                distance_km=1200,
                rsrp_dbm=-88,
                link_margin_db=32,
                sat_load=0.3,
                remaining_visible_s=300,
            ),
            Candidate(
                sat_id=11,
                elevation_deg=10,
                distance_km=1500,
                rsrp_dbm=-95,
                link_margin_db=25,
                sat_load=0.8,
                remaining_visible_s=120,
                handover_penalty=1,
            ),
        ],
    )
    response = score(request)
    assert response.selected_sat_id in {10, 11}
    assert len(response.scores) == 2
    assert response.scores[0].rank == 1
    assert "Synthetic demo" in response.notice
