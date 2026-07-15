from pathlib import Path

import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline, FeatureUnion

from src.feature_engineering import ManualFeatureExtractor, extract_manual_features


BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = BASE_DIR / "data" / "labeled_calls.csv"
MODEL_PATH = BASE_DIR / "models" / "risk_classifier.joblib"


def train_risk_classifier():
    df = pd.read_csv(DATA_PATH)

    X = df["transcript"]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y
    )

    model = Pipeline([
        ("features", FeatureUnion([
            ("tfidf", TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2)
            )),
            ("manual_features", ManualFeatureExtractor())
        ])),
        ("classifier", LogisticRegression(
            max_iter=1000,
            class_weight="balanced"
        ))
    ])

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)

    print("Accuracy:", round(accuracy, 3))
    print()
    print(classification_report(y_test, predictions, zero_division=0))

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print(f"Model saved to {MODEL_PATH}")


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "Model not found. Run: python scripts/train_model.py"
        )

    return joblib.load(MODEL_PATH)


def apply_hybrid_risk_rules(ml_prediction, manual_features):
    final_prediction = ml_prediction
    decision_reason = "Used ML model prediction."

    if (
        manual_features["fraud_keyword_count"] >= 2
        and manual_features["compliance_keyword_count"] == 0
    ):
        final_prediction = "Fraud Risk"

        if ml_prediction == "Fraud Risk":
            decision_reason = "ML prediction confirmed by multiple fraud-risk signals."
        else:
            decision_reason = "Overrode ML prediction because transcript contains multiple fraud-risk signals."

    elif manual_features["compliance_keyword_count"] >= 2:
        final_prediction = "Compliance Risk"

        if ml_prediction == "Compliance Risk":
            decision_reason = "ML prediction confirmed by multiple compliance-risk signals."
        else:
            decision_reason = "Overrode ML prediction because transcript contains multiple compliance-risk signals."

    elif (
        manual_features["escalation_keyword_count"] >= 2
        or manual_features["urgency_word_count"] >= 2
    ):
        final_prediction = "Escalation Risk"

        if ml_prediction == "Escalation Risk":
            decision_reason = "ML prediction confirmed by escalation or urgency signals."
        else:
            decision_reason = "Overrode ML prediction because transcript contains escalation or urgency signals."

    elif (
        manual_features["support_keyword_count"] >= 2
        and manual_features["risk_keyword_total"] == 0
    ):
        final_prediction = "Normal Support"

        if ml_prediction == "Normal Support":
            decision_reason = "ML prediction confirmed by routine support signals."
        else:
            decision_reason = "Overrode ML prediction because transcript appears to be routine support."

    return final_prediction, decision_reason


def predict_risk(transcript):
    model = load_model()

    ml_prediction = model.predict([transcript])[0]

    probabilities = model.predict_proba([transcript])[0]
    classes = model.classes_

    probability_map = {
        label: round(float(probability), 4)
        for label, probability in zip(classes, probabilities)
    }

    manual_features = extract_manual_features(transcript)

    final_prediction, decision_reason = apply_hybrid_risk_rules(
        ml_prediction,
        manual_features
    )

    return {
        "ml_prediction": ml_prediction,
        "final_prediction": final_prediction,
        "decision_reason": decision_reason,
        "probabilities": probability_map,
        "manual_features": manual_features
    }
