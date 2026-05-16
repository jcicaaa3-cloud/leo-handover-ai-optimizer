from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, average_precision_score, roc_auc_score
from sklearn.pipeline import Pipeline

from .features import FEATURE_COLUMNS, build_xy, validate_candidate_frame


def temporal_train_test_split(
    frame: pd.DataFrame,
    test_fraction: float = 0.25,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split by timestep to mimic future decision epochs."""

    validate_candidate_frame(frame, require_target=True)
    if not 0.0 < test_fraction < 1.0:
        raise ValueError("test_fraction must be between 0 and 1")

    timesteps = np.array(sorted(frame["timestep"].unique()))
    split_index = max(1, int(len(timesteps) * (1.0 - test_fraction)))
    if split_index >= len(timesteps):
        split_index = len(timesteps) - 1
    train_steps = set(timesteps[:split_index])
    train = frame[frame["timestep"].isin(train_steps)].copy()
    test = frame[~frame["timestep"].isin(train_steps)].copy()
    if train.empty or test.empty:
        raise ValueError("Temporal split produced an empty train or test set")
    return train, test


def make_model(random_state: int = 42) -> Pipeline:
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=160,
                    max_depth=10,
                    min_samples_leaf=2,
                    class_weight="balanced_subsample",
                    random_state=random_state,
                    n_jobs=1,
                ),
            ),
        ]
    )


def predict_candidate_scores(model_bundle: dict[str, Any], frame: pd.DataFrame) -> np.ndarray:
    feature_columns = model_bundle.get("feature_columns", FEATURE_COLUMNS)
    model = model_bundle["model"]
    probabilities = model.predict_proba(frame[feature_columns])
    classes = list(model.classes_)
    positive_index = classes.index(1) if 1 in classes else int(np.argmax(classes))
    return probabilities[:, positive_index]


def _top1_accuracy(model_bundle: dict[str, Any], frame: pd.DataFrame) -> float:
    scored = frame.copy()
    scored["ai_score"] = predict_candidate_scores(model_bundle, scored)
    chosen = scored.loc[scored.groupby(["user_id", "timestep"])["ai_score"].idxmax()]
    return float(chosen["selected"].mean())


def train_handover_model(
    frame: pd.DataFrame,
    random_state: int = 42,
    test_fraction: float = 0.25,
) -> dict[str, Any]:
    train, test = temporal_train_test_split(frame, test_fraction=test_fraction)
    x_train, y_train = build_xy(train)
    x_test, y_test = build_xy(test)

    model = make_model(random_state=random_state)
    model.fit(x_train, y_train)
    bundle: dict[str, Any] = {
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "metadata": {
            "random_state": random_state,
            "test_fraction": test_fraction,
            "train_rows": int(len(train)),
            "test_rows": int(len(test)),
            "test_timestep_min": int(test["timestep"].min()),
            "feature_columns": FEATURE_COLUMNS,
        },
    }

    y_score = predict_candidate_scores(bundle, test)
    y_pred = (y_score >= 0.5).astype(int)
    metrics = {
        "candidate_accuracy": float(accuracy_score(y_test, y_pred)),
        "top1_decision_accuracy": _top1_accuracy(bundle, test),
    }
    # AUC metrics need both classes. The simulator usually provides both, but
    # the guard keeps small smoke tests safe.
    if len(set(y_test)) == 2:
        metrics["roc_auc"] = float(roc_auc_score(y_test, y_score))
        metrics["average_precision"] = float(average_precision_score(y_test, y_score))
    bundle["metadata"]["validation_metrics"] = metrics
    return bundle


def feature_importances(model_bundle: dict[str, Any]) -> pd.DataFrame:
    model = model_bundle["model"].named_steps["model"]
    importances = getattr(model, "feature_importances_", None)
    if importances is None:
        raise ValueError("The model does not expose feature_importances_")
    return pd.DataFrame(
        {"feature": model_bundle.get("feature_columns", FEATURE_COLUMNS), "importance": importances}
    ).sort_values("importance", ascending=False)


def save_model(model_bundle: dict[str, Any], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_bundle, path)


def load_model(path: str | Path) -> dict[str, Any]:
    bundle = joblib.load(path)
    if isinstance(bundle, dict) and "model" in bundle:
        return bundle
    return {"model": bundle, "feature_columns": FEATURE_COLUMNS, "metadata": {}}
