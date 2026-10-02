
import math
import pandas as pd


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    work["disaster_type"] = work["disaster_type"].astype(str).str.upper()
    work["people_affected"] = work["people_affected"].astype(int)
    work["injuries"] = work["injuries"].astype(int)

    work["log_people_affected"] = work["people_affected"].apply(lambda x: round(math.log1p(max(x, 0)), 6))
    work["injury_ratio"] = work.apply(
        lambda row: round(row["injuries"] / max(row["people_affected"], 1), 6), axis=1
    )
    work["severity_pressure"] = (work["people_affected"] * 0.015) + (work["injuries"] * 0.25)
    work["critical_flag"] = ((work["people_affected"] >= 200) | (work["injuries"] >= 20)).astype(int)

    type_risk = {
        "EARTHQUAKE": 1.35,
        "INDUSTRIAL_FIRE": 1.30,
        "WILDFIRE": 1.25,
        "CYCLONE": 1.20,
        "FLOOD": 1.15,
        "LANDSLIDE": 1.05,
        "STORM": 1.0,
        "DROUGHT": 0.95,
    }
    work["type_risk"] = work["disaster_type"].map(type_risk).fillna(1.0)

    encoded = pd.get_dummies(work[["disaster_type"]], columns=["disaster_type"])
    features = pd.concat(
        [
            work[[
                "people_affected",
                "injuries",
                "log_people_affected",
                "injury_ratio",
                "severity_pressure",
                "critical_flag",
                "type_risk",
            ]],
            encoded,
        ],
        axis=1,
    )
    return features
