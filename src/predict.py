"""Classify a user query with the saved baseline model.

Usage (command line):
    python src/predict.py "My landlord has refused to return my security deposit."

Usage (Python, e.g. inside a future FastAPI/Flask endpoint):
    from predict import predict
    predict("My employer has not paid my salary")
"""
import json
import sys
from functools import lru_cache
from pathlib import Path

import joblib

from text_utils import clean_text

MODEL_FILE = Path(__file__).resolve().parents[1] / "models" / "baseline_classifier.joblib"
OUT_OF_SCOPE = "other_out_of_scope"


@lru_cache(maxsize=1)
def load_model(path: str = str(MODEL_FILE)) -> dict:
    return joblib.load(path)


def predict(query: str) -> dict:
    """Return the predicted category, its confidence and whether clarification is needed.

    needs_clarification is True when the query is out of scope or the confidence is below
    the threshold chosen on the validation set. The chatbot should then ask the user to
    rephrase or refer them to a professional instead of continuing.
    """
    bundle = load_model()
    model, threshold = bundle["pipeline"], bundle["threshold"]
    text = clean_text(query)
    if not text:
        return {"category": OUT_OF_SCOPE, "confidence": 0.0, "top_3": [],
                "needs_clarification": True, "threshold": threshold}

    proba = model.predict_proba([text])[0]
    ranked = sorted(zip(model.classes_, proba), key=lambda p: p[1], reverse=True)
    category, confidence = ranked[0]
    return {
        "category": str(category),
        "confidence": round(float(confidence), 4),
        "top_3": [{"category": str(c), "confidence": round(float(p), 4)} for c, p in ranked[:3]],
        "needs_clarification": bool(category == OUT_OF_SCOPE or confidence < threshold),
        "threshold": threshold,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('Usage: python src/predict.py "your legal question"')
    print(json.dumps(predict(" ".join(sys.argv[1:])), indent=2))
