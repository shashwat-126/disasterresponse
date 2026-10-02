
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

from app.model_registry import ensure_parent_dirs, settings
from app.preprocess import prepare_features


def _evaluate(model, X_test, y_test, class_names: list[str]) -> dict:
    predictions = model.predict(X_test)
    report = classification_report(
        y_test, predictions, target_names=class_names, output_dict=True, zero_division=0
    )
    return {
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "weighted_f1": round(float(f1_score(y_test, predictions, average="weighted")), 4),
        # Per-class precision/recall/f1 — CRITICAL recall matters most operationally: a
        # false negative there means an emergency gets triaged as routine.
        "per_class": {
            name: {
                "precision": round(report[name]["precision"], 4),
                "recall": round(report[name]["recall"], 4),
                "f1": round(report[name]["f1-score"], 4),
                "support": int(report[name]["support"]),
            }
            for name in class_names
        },
    }


def train() -> None:
    ensure_parent_dirs()
    data_path = Path(settings.training_data_path)
    if not data_path.exists():
        raise FileNotFoundError(f"Training data not found at {data_path}")

    df = pd.read_csv(data_path)
    X = prepare_features(df)
    y_raw = df["severity"].astype(str).str.upper()

    encoder = LabelEncoder()
    y = encoder.fit_transform(y_raw)
    class_names = encoder.classes_.tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=240,
        max_depth=12,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    rf_metrics = _evaluate(model, X_test, y_test, class_names)

    # Baseline comparison: a plain multinomial logistic regression on the same split and
    # features, scaled (LR is scale-sensitive, unlike the tree model). This is what
    # justifies picking RandomForest over a simpler linear model rather than assuming it.
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    baseline = LogisticRegression(max_iter=2000, class_weight="balanced", multi_class="auto")
    baseline.fit(X_train_scaled, y_train)
    baseline_metrics = _evaluate(baseline, X_test_scaled, y_test, class_names)

    joblib.dump({"model": model, "feature_columns": list(X.columns)}, settings.model_path)
    joblib.dump(encoder, settings.label_encoder_path)

    metadata = {
        "model_version": "rf-risk-v2",
        "classes": class_names,
        "feature_columns": list(X.columns),
        "training_rows": int(len(df)),
        "test_rows": int(len(X_test)),
        "metrics": {
            "accuracy": rf_metrics["accuracy"],
            "weighted_f1": rf_metrics["weighted_f1"],
        },
        "classification_report": rf_metrics["per_class"],
        "baseline_comparison": {
            "model": "LogisticRegression",
            "accuracy": baseline_metrics["accuracy"],
            "weighted_f1": baseline_metrics["weighted_f1"],
            "per_class": baseline_metrics["per_class"],
            "delta_weighted_f1_vs_random_forest": round(rf_metrics["weighted_f1"] - baseline_metrics["weighted_f1"], 4),
        },
    }
    Path(settings.metadata_path).write_text(json.dumps(metadata, indent=2), encoding="utf-8")


if __name__ == "__main__":
    train()
