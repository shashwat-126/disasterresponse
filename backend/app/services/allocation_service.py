import math

from app.models.allocation import Allocation

# Base quantities per severity tier — the floor for that tier regardless of headcount.
ALLOCATION_RULES = {
    "LOW": {"ambulances": 1, "rescue_teams": 1, "vehicles": 2, "food_kits": 25, "water_liters": 500, "shelters": 0, "notes": "Monitor locally."},
    "MEDIUM": {"ambulances": 2, "rescue_teams": 2, "vehicles": 4, "food_kits": 100, "water_liters": 2000, "shelters": 1, "notes": "District response needed."},
    "HIGH": {"ambulances": 4, "rescue_teams": 4, "vehicles": 8, "food_kits": 300, "water_liters": 6000, "shelters": 2, "notes": "Multi-agency coordination advised."},
    "CRITICAL": {"ambulances": 8, "rescue_teams": 8, "vehicles": 16, "food_kits": 1000, "water_liters": 20000, "shelters": 5, "notes": "Emergency command activation recommended."},
}


PEOPLE_PER_UNIT = {
    "ambulances": 40,
    "rescue_teams": 60,
    "vehicles": 30,
    "food_kits": 1,  # ~1 kit per affected person
    "water_liters": 4,  # ~4L per affected person per day
    "shelters": 150,
}


def build_allocation(incident_id: int, severity: str, people_affected: int = 0, risk_score: float = 0.0) -> Allocation:
    """Blend the static severity-tier floor with headcount- and risk-score-driven scaling.

    - The severity tier still sets a sensible floor (a CRITICAL incident never gets a LOW
      allocation, even with a small reported headcount).
    - `people_affected` scales quantities up for large-scale incidents within the same tier.
    - `risk_score` (0-100, from the ML service) nudges the multiplier further for incidents
      the model considers unusually severe within their tier, e.g. a HIGH incident sitting at
      risk_score=88 gets more than one sitting at risk_score=62.
    """
    normalized = (severity or "MEDIUM").upper()
    rule = dict(ALLOCATION_RULES.get(normalized, ALLOCATION_RULES["MEDIUM"]))

    # Risk multiplier: 1.0x at risk_score=0, up to ~1.5x at risk_score=100.
    risk_multiplier = 1.0 + max(0.0, min(100.0, risk_score)) / 200.0

    for field, per_unit in PEOPLE_PER_UNIT.items():
        floor = rule[field]
        headcount_driven = math.ceil((people_affected * risk_multiplier) / per_unit) if per_unit else 0
        rule[field] = max(floor, headcount_driven)

    return Allocation(incident_id=incident_id, **rule)
