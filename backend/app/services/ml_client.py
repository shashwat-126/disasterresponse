from typing import Any

import httpx

from app.core.config import get_settings

SEVERITY_RISK_BASE = {"LOW": 15, "MEDIUM": 40, "HIGH": 68, "CRITICAL": 90}
SEVERITY_PRIORITY = {"LOW": "P4", "MEDIUM": "P3", "HIGH": "P2", "CRITICAL": "P1"}
SEVERITY_ETA_MINUTES = {"LOW": 240, "MEDIUM": 90, "HIGH": 35, "CRITICAL": 15}


def _local_fallback(disaster_type: str, people_affected: int, injuries: int) -> dict[str, Any]:
    """Used only if the ML microservice itself cannot be reached at all."""
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

    if score >= 6:
        severity = "CRITICAL"
    elif score >= 4:
        severity = "HIGH"
    elif score >= 2:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    return {
        "severity": severity,
        "confidence": 0.5,
        "model_version": "backend-fallback-v1",
        "fallback_used": True,
        "risk_score": float(SEVERITY_RISK_BASE.get(severity, 40)),
        "priority_level": SEVERITY_PRIORITY.get(severity, "P3"),
        "estimated_response_minutes": SEVERITY_ETA_MINUTES.get(severity, 90),
        "secondary_hazards": ["ML service unreachable; secondary hazard analysis unavailable"],
        "immediate_recommendations": ["ML service unreachable; apply standard response protocol for " + severity],
        "explanation_summary": "Backend fallback heuristic (ML service unreachable).",
        "top_signals": [],
    }


def predict_severity(payload: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.post(f"{settings.ml_service_url}/predict", json=payload)
            response.raise_for_status()
            data = response.json()
            explanations = data.get("explanations") or {}
            return {
                "severity": str(data.get("severity", "MEDIUM")).upper(),
                "confidence": float(data.get("confidence", 0.5)),
                "model_version": str(data.get("model_version", "ml-v1")),
                "fallback_used": bool(data.get("fallback_used", False)),
                "risk_score": float(data.get("risk_score", 40.0)),
                "priority_level": str(data.get("priority_level", "P3")),
                "estimated_response_minutes": int(data.get("estimated_response_minutes", 90)),
                "secondary_hazards": list(data.get("secondary_hazards", [])),
                "immediate_recommendations": list(data.get("immediate_recommendations", [])),
                "explanation_summary": str(explanations.get("summary", "")),
                "top_signals": list(explanations.get("top_signals", [])),
            }
    except Exception:
        return _local_fallback(
            str(payload.get("disaster_type", "")),
            int(payload.get("people_affected", 0)),
            int(payload.get("injuries", 0)),
        )
