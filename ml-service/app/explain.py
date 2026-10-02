
from typing import Any


def explain_prediction(disaster_type: str, people_affected: int, injuries: int) -> dict[str, Any]:
    signals: list[str] = []
    dtype = disaster_type.upper()
    if people_affected >= 250:
        signals.append("Large affected population")
    elif people_affected >= 100:
        signals.append("Moderate-to-high affected population")
    if injuries >= 20:
        signals.append("High injury count")
    elif injuries >= 7:
        signals.append("Meaningful injury count")
    if dtype in {"EARTHQUAKE", "WILDFIRE", "INDUSTRIAL_FIRE"}:
        signals.append(f"{dtype.title().replace('_', ' ')} risk profile")
    if not signals:
        signals.append("Lower reported operational pressure")
    return {
        "top_signals": signals[:3],
        "summary": "; ".join(signals[:3]),
    }


SEVERITY_RISK_BASE = {"LOW": 15, "MEDIUM": 40, "HIGH": 68, "CRITICAL": 90}

SEVERITY_PRIORITY = {"LOW": "P4", "MEDIUM": "P3", "HIGH": "P2", "CRITICAL": "P1"}

SEVERITY_ETA_MINUTES = {"LOW": 240, "MEDIUM": 90, "HIGH": 35, "CRITICAL": 15}

SECONDARY_HAZARDS = {
    "flood": ["Waterborne disease outbreak", "Contaminated drinking water", "Electrical hazards from submerged lines"],
    "earthquake": ["Aftershocks", "Structural collapse of weakened buildings", "Gas line ruptures / fire risk"],
    "landslide": ["Further slope failure", "Blocked access roads", "Debris flow into waterways"],
    "cyclone": ["Storm surge flooding", "Downed power lines", "Wind-driven secondary fires"],
    "fire": ["Toxic smoke inhalation", "Structural collapse", "Fire spread to adjacent structures"],
    "industrial_accident": ["Chemical exposure", "Explosion risk", "Groundwater contamination"],
    "epidemic": ["Healthcare system overload", "Secondary infections", "Supply chain disruption"],
}

IMMEDIATE_RECOMMENDATIONS = {
    "LOW": ["Monitor the situation", "Keep local contacts informed", "Prepare basic supplies as a precaution"],
    "MEDIUM": ["Dispatch a district response team", "Set up a local coordination point", "Begin needs assessment"],
    "HIGH": ["Activate multi-agency coordination", "Pre-position medical and rescue resources", "Issue public safety alerts"],
    "CRITICAL": [
        "Activate emergency command center immediately",
        "Deploy all available rescue and medical resources",
        "Coordinate evacuation where necessary",
        "Issue critical public alerts across all channels",
    ],
}


def enrich_prediction(disaster_type: str, severity: str, people_affected: int, injuries: int, confidence: float) -> dict[str, Any]:
    """Rule-based enrichment layered on top of the severity classification.

    Kept separate from the ML classifier itself so it can be tuned independently
    and reproduced identically by the backend's fallback path if this service
    is unreachable.
    """
    severity = (severity or "MEDIUM").upper()
    dtype_key = (disaster_type or "").strip().lower().replace(" ", "_")

    base_risk = SEVERITY_RISK_BASE.get(severity, 40)
    # Nudge risk score within its severity band using the underlying signals.
    pressure = min(people_affected / 20 + injuries * 1.5, 25)
    risk_score = round(min(base_risk + pressure * 0.4 - (1 - confidence) * 10, 100), 1)
    risk_score = max(risk_score, 0.0)

    secondary_hazards = SECONDARY_HAZARDS.get(dtype_key, ["Situation may evolve; reassess as new information arrives"])
    recommendations = IMMEDIATE_RECOMMENDATIONS.get(severity, IMMEDIATE_RECOMMENDATIONS["MEDIUM"])

    return {
        "risk_score": risk_score,
        "priority_level": SEVERITY_PRIORITY.get(severity, "P3"),
        "estimated_response_minutes": SEVERITY_ETA_MINUTES.get(severity, 90),
        "secondary_hazards": secondary_hazards,
        "immediate_recommendations": recommendations,
    }
