
import json
from pathlib import Path

import joblib
import pandas as pd

from app.explain import enrich_prediction, explain_prediction
from app.model_registry import settings
from app.preprocess import prepare_features


class Predictor:
    def __init__(self) -> None:
        self.bundle = None
        self.encoder = None
        self.metadata = {"model_version": "fallback-v1", "metrics": {}}
        self._load()

    def _load(self) -> None:
        model_path = Path(settings.model_path)
        encoder_path = Path(settings.label_encoder_path)
        metadata_path = Path(settings.metadata_path)

        if model_path.exists() and encoder_path.exists():
            self.bundle = joblib.load(model_path)
            self.encoder = joblib.load(encoder_path)
        if metadata_path.exists():
            self.metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    def predict(self, disaster_type: str, people_affected: int, injuries: int) -> dict:
        disaster_type = disaster_type.upper()

        if self.bundle is None or self.encoder is None:
            severity = self._fallback(disaster_type, people_affected, injuries)
            confidence = 0.55
            return {
                "severity": severity,
                "confidence": confidence,
                "model_version": "fallback-v1",
                "fallback_used": True,
                "metrics": {},
                "explanations": explain_prediction(disaster_type, people_affected, injuries),
                **enrich_prediction(disaster_type, severity, people_affected, injuries, confidence),
            }

        row = pd.DataFrame([{"disaster_type": disaster_type, "people_affected": people_affected, "injuries": injuries}])
        X = prepare_features(row)
        expected = self.bundle["feature_columns"]
        for col in expected:
            if col not in X.columns:
                X[col] = 0
        X = X[expected]

        model = self.bundle["model"]
        pred_idx = model.predict(X)[0]
        probabilities = model.predict_proba(X)[0]
        confidence = float(max(probabilities))
        severity = str(self.encoder.inverse_transform([pred_idx])[0]).upper()

        return {
            "severity": severity,
            "confidence": round(confidence, 4),
            "model_version": self.metadata.get("model_version", "rf-risk-v2"),
            "fallback_used": False,
            "metrics": self.metadata.get("metrics", {}),
            "explanations": explain_prediction(disaster_type, people_affected, injuries),
            **enrich_prediction(disaster_type, severity, people_affected, injuries, confidence),
        }

    @staticmethod
    def _fallback(disaster_type: str, people_affected: int, injuries: int) -> str:
        score = 0
        if people_affected >= 300:
            score += 3
        elif people_affected >= 120:
            score += 2
        elif people_affected >= 40:
            score += 1
        if injuries >= 30:
            score += 3
        elif injuries >= 10:
            score += 2
        elif injuries >= 3:
            score += 1
        if disaster_type in {"EARTHQUAKE", "WILDFIRE", "FLOOD", "INDUSTRIAL_FIRE"}:
            score += 1
        if score >= 6:
            return "CRITICAL"
        if score >= 4:
            return "HIGH"
        if score >= 2:
            return "MEDIUM"
        return "LOW"
