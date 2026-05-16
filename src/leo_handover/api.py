from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .explainability import explain_epoch
from .features import FEATURE_COLUMNS
from .models import load_model, predict_candidate_scores

PROJECT_NOTICE = "Synthetic demo data only. Not validated for real satellite-network operations."


class Candidate(BaseModel):
    sat_id: int
    elevation_deg: float
    distance_km: float
    rsrp_dbm: float
    link_margin_db: float
    sat_load: float = Field(ge=0.0, le=1.0)
    remaining_visible_s: float
    relative_velocity_km_s: float = 7.6
    is_current_sat: int = 0
    handover_penalty: int = 0
    candidate_rank_signal: int = 0
    demand_mbps: float = 10.0
    time_sin: float = 0.0
    time_cos: float = 1.0


class ScoreRequest(BaseModel):
    user_id: int = 0
    timestep: int = 0
    candidates: list[Candidate]


class CandidateScore(BaseModel):
    rank: int
    sat_id: int
    score: float


class ScoreResponse(BaseModel):
    selected_sat_id: int
    policy: str
    notice: str
    scores: list[CandidateScore]


app = FastAPI(title="LEO Handover AI Optimizer", version="0.2.0")
_MODEL_BUNDLE: dict[str, Any] | None = None


def _model_path() -> Path:
    return Path(os.environ.get("LEO_HANDOVER_MODEL", "artifacts/handover_model.joblib"))


def _get_model() -> dict[str, Any] | None:
    global _MODEL_BUNDLE
    if _MODEL_BUNDLE is not None:
        return _MODEL_BUNDLE
    path = _model_path()
    if path.exists():
        _MODEL_BUNDLE = load_model(path)
    return _MODEL_BUNDLE


def _request_frame(request: ScoreRequest) -> pd.DataFrame:
    if not request.candidates:
        raise HTTPException(status_code=400, detail="At least one candidate is required")
    frame = pd.DataFrame([candidate.model_dump() for candidate in request.candidates])
    frame["user_id"] = request.user_id
    frame["timestep"] = request.timestep
    return frame


def _fallback_score(frame: pd.DataFrame) -> pd.Series:
    # Deployment-style fallback if the model artifact is not present yet.
    # It is still only a transparent demo heuristic, not a production controller.
    return (
        0.055 * frame["link_margin_db"]
        + 0.006 * frame["remaining_visible_s"]
        + 0.020 * frame["elevation_deg"]
        - 1.050 * frame["sat_load"]
        - 0.450 * frame["handover_penalty"]
    )


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {"status": "ok", "model_loaded": _get_model() is not None, "notice": PROJECT_NOTICE}


@app.post("/score", response_model=ScoreResponse)
def score(request: ScoreRequest) -> ScoreResponse:
    frame = _request_frame(request)
    bundle = _get_model()
    if bundle is not None:
        scores = predict_candidate_scores(bundle, frame)
        policy = "ai_ranker"
    else:
        scores = _fallback_score(frame).to_numpy()
        policy = "fallback_load_aware"

    ranked = frame.assign(score=scores).sort_values("score", ascending=False).reset_index(drop=True)
    chosen = ranked.iloc[0]
    return ScoreResponse(
        selected_sat_id=int(chosen["sat_id"]),
        policy=policy,
        notice=PROJECT_NOTICE,
        scores=[
            CandidateScore(rank=int(index + 1), sat_id=int(row.sat_id), score=float(row.score))
            for index, row in enumerate(ranked.itertuples(index=False))
        ],
    )


@app.post("/explain")
def explain(request: ScoreRequest) -> dict[str, Any]:
    frame = _request_frame(request)
    return explain_epoch(frame, model_bundle=_get_model(), user_id=request.user_id, timestep=request.timestep)
