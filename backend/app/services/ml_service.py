"""
ml_service.py – Match Outcome Prediction ML Service

Uses scikit-learn RandomForestClassifier when available.
Falls back to a pure-NumPy Naive Bayes + weighted heuristic model when
sklearn C-extensions are blocked by system policy.
"""
import os
import json
import joblib
import numpy as np
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.match import Match
from app.services.feature_engine import compute_features, get_feature_names
from app.config import settings

FEATURE_NAMES = get_feature_names()
OUTCOME_MAP = {"team_a": 0, "draw": 1, "team_b": 2}
REV_OUTCOME_MAP = {0: "team_a", 1: "draw", 2: "team_b"}

# ------------------------------------------------------------------
# Pure-NumPy Gaussian Naive Bayes (fallback when sklearn is blocked)
# ------------------------------------------------------------------
class NaiveBayesClassifier:
    """Simple Gaussian Naive Bayes – no C extensions required."""

    def __init__(self):
        self.class_log_prior_ = None
        self.theta_ = None    # means per class
        self.sigma_ = None    # variances per class
        self.classes_ = None
        self.feature_importances_ = None

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.classes_ = np.unique(y)
        n_classes = len(self.classes_)
        n_features = X.shape[1]
        self.theta_ = np.zeros((n_classes, n_features))
        self.sigma_ = np.zeros((n_classes, n_features))
        counts = np.zeros(n_classes)
        for i, c in enumerate(self.classes_):
            X_c = X[y == c]
            counts[i] = len(X_c)
            self.theta_[i] = X_c.mean(axis=0)
            self.sigma_[i] = X_c.var(axis=0) + 1e-9
        self.class_log_prior_ = np.log(counts / counts.sum())
        # Feature importance ≈ variance of class means (discriminative power)
        var_of_means = self.theta_.var(axis=0)
        self.feature_importances_ = var_of_means / (var_of_means.sum() + 1e-9)
        return self

    def _log_likelihood(self, X: np.ndarray):
        n_classes = len(self.classes_)
        ll = np.zeros((X.shape[0], n_classes))
        for i in range(n_classes):
            diff = X - self.theta_[i]
            ll[:, i] = -0.5 * np.sum(
                np.log(2 * np.pi * self.sigma_[i]) + diff ** 2 / self.sigma_[i],
                axis=1
            )
        return ll

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        log_proba = self._log_likelihood(X) + self.class_log_prior_
        # Softmax
        log_proba -= log_proba.max(axis=1, keepdims=True)
        proba = np.exp(log_proba)
        proba /= proba.sum(axis=1, keepdims=True)
        return proba

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.classes_[np.argmax(self.predict_proba(X), axis=1)]


class StandardScaler:
    """Pure-NumPy StandardScaler."""

    def __init__(self):
        self.mean_ = None
        self.std_ = None

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        self.mean_ = X.mean(axis=0)
        self.std_ = X.std(axis=0) + 1e-9
        return (X - self.mean_) / self.std_

    def transform(self, X: np.ndarray) -> np.ndarray:
        return (X - self.mean_) / self.std_


# ------------------------------------------------------------------
# Try importing sklearn; use fallback if DLL policy blocks it
# ------------------------------------------------------------------
_USE_SKLEARN = False
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler as SKStandardScaler
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
    _USE_SKLEARN = True
except ImportError:
    pass


# ------------------------------------------------------------------
# ML Service
# ------------------------------------------------------------------
class MLService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.metadata = None
        self._use_sklearn = _USE_SKLEARN
        self._load_model()

    def _load_model(self):
        if os.path.exists(settings.MODEL_PATH) and os.path.exists(settings.MODEL_METADATA_PATH):
            try:
                saved = joblib.load(settings.MODEL_PATH)
                if self._use_sklearn and hasattr(saved, 'predict_proba'):
                    # It's a sklearn pipeline
                    self.model = saved
                    self.scaler = None
                elif isinstance(saved, dict) and "model" in saved:
                    self.model = saved["model"]
                    self.scaler = saved.get("scaler")
                with open(settings.MODEL_METADATA_PATH, "r") as f:
                    self.metadata = json.load(f)
            except Exception:
                self.model = None

    def is_trained(self) -> bool:
        return self.model is not None

    def train(self, db_session: Session) -> Dict[str, Any]:
        matches = db_session.query(Match).filter(
            Match.is_completed == True, Match.outcome != None
        ).all()
        if len(matches) < 10:
            return {"error": "Not enough data to train"}

        X_list, y_list = [], []
        for m in matches:
            try:
                feats = compute_features(db_session, m.team_a, m.team_b, m.venue)
                X_list.append([feats[f] for f in FEATURE_NAMES])
                y_list.append(OUTCOME_MAP[m.outcome])
            except Exception:
                continue

        X = np.array(X_list, dtype=float)
        y = np.array(y_list, dtype=int)

        # 80/20 split (manual, no sklearn required)
        n = len(X)
        split = int(n * 0.8)
        indices = np.random.RandomState(42).permutation(n)
        X_train, X_test = X[indices[:split]], X[indices[split:]]
        y_train, y_test = y[indices[:split]], y[indices[split:]]

        os.makedirs(os.path.dirname(settings.MODEL_PATH), exist_ok=True)

        if self._use_sklearn:
            pipeline = Pipeline([
                ("scaler", SKStandardScaler()),
                ("classifier", RandomForestClassifier(
                    n_estimators=200, random_state=42, class_weight="balanced"
                ))
            ])
            pipeline.fit(X_train, y_train)
            y_pred = pipeline.predict(X_test)
            acc = float((y_pred == y_test).mean())
            self.model = pipeline
            self.scaler = None
            joblib.dump(pipeline, settings.MODEL_PATH)
        else:
            # Pure-NumPy fallback
            scaler = StandardScaler()
            X_train_s = scaler.fit_transform(X_train)
            X_test_s = scaler.transform(X_test)
            clf = NaiveBayesClassifier()
            clf.fit(X_train_s, y_train)
            y_pred = clf.predict(X_test_s)
            acc = float((y_pred == y_test).mean())
            self.model = clf
            self.scaler = scaler
            joblib.dump({"model": clf, "scaler": scaler}, settings.MODEL_PATH)

        self.metadata = {
            "feature_names": FEATURE_NAMES,
            "classes": ["team_a", "draw", "team_b"],
            "training_date": datetime.now().isoformat(),
            "num_samples": len(X_list),
            "test_accuracy": acc,
            "backend": "sklearn_rf" if self._use_sklearn else "numpy_gnb",
        }
        with open(settings.MODEL_METADATA_PATH, "w") as f:
            json.dump(self.metadata, f)

        return {
            "status": "success",
            "metrics": {"accuracy": acc},
            "samples_trained": len(X_list),
            "test_accuracy": acc,
            "num_samples": len(X_list),
            "training_date": self.metadata["training_date"],
            "backend": self.metadata["backend"],
        }

    def predict(self, features_dict: Dict[str, float]) -> Dict[str, Any]:
        if not self.is_trained():
            raise RuntimeError("Model is not trained")

        x_input = np.array([[features_dict.get(f, 0.0) for f in FEATURE_NAMES]])

        if self._use_sklearn and self.scaler is None:
            # sklearn pipeline handles scaling internally
            probs = self.model.predict_proba(x_input)[0]
            importances = self.model.named_steps["classifier"].feature_importances_
        else:
            x_scaled = self.scaler.transform(x_input)
            probs = self.model.predict_proba(x_scaled)[0]
            importances = self.model.feature_importances_

        # Ensure probability order matches [team_a=0, draw=1, team_b=2]
        if self._use_sklearn:
            classes = list(self.model.classes_)
        else:
            classes = list(self.model.classes_)
        prob_ordered = np.zeros(3)
        for i, c in enumerate(classes):
            prob_ordered[c] = probs[i]

        indices = np.argsort(importances)[::-1][:5]
        top_features = [
            {"feature_name": FEATURE_NAMES[i], "importance": float(importances[i])}
            for i in indices
        ]

        predicted_idx = int(np.argmax(prob_ordered))
        return {
            "predicted_outcome": REV_OUTCOME_MAP[predicted_idx],
            "prob_team_a": float(prob_ordered[0]),
            "prob_draw": float(prob_ordered[1]),
            "prob_team_b": float(prob_ordered[2]),
            "confidence": float(np.max(prob_ordered)),
            "top_features": top_features,
        }

    def get_feature_importances(self) -> List[Dict[str, Any]]:
        if not self.is_trained():
            return []
        if self._use_sklearn and self.scaler is None:
            importances = self.model.named_steps["classifier"].feature_importances_
        else:
            importances = self.model.feature_importances_
        res = [
            {"feature_name": f, "importance": float(imp)}
            for f, imp in zip(FEATURE_NAMES, importances)
        ]
        res.sort(key=lambda x: x["importance"], reverse=True)
        return res


ml_service = MLService()
