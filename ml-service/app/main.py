
from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.predict import Predictor

app = FastAPI(title="EADRP ML Service")
predictor = Predictor()


class PredictRequest(BaseModel):
    disaster_type: str
    people_affected: int = Field(ge=0)
    injuries: int = Field(ge=0)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_ready": predictor.bundle is not None,
        "model_version": predictor.metadata.get("model_version", "fallback-v1"),
        "metrics": predictor.metadata.get("metrics", {}),
    }


@app.post("/predict")
def predict(payload: PredictRequest):
    return predictor.predict(
        disaster_type=payload.disaster_type,
        people_affected=payload.people_affected,
        injuries=payload.injuries,
    )
