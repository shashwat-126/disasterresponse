from pathlib import Path
import sys

ML_SERVICE_ROOT = str(Path(__file__).resolve().parents[2] / "ml-service")

# backend/app and ml-service/app share the module name "app". If backend's test
# modules already ran in this session, sys.modules["app"] points at backend/app
# and this import would silently resolve to the wrong package. Purge any cached
# "app" modules first so this import is served fresh from ml-service/app.
for name in list(sys.modules):
    if name == "app" or name.startswith("app."):
        del sys.modules[name]

sys.path.insert(0, ML_SERVICE_ROOT)

from app.predict import Predictor  # noqa: E402


def test_predictor_returns_shape():
    predictor = Predictor()
    result = predictor.predict("flood", 100, 10)
    assert "severity" in result
    assert "confidence" in result
