"""Train and evaluate the baseline legal query classifier.

1. Compare a majority-class dummy, Multinomial Naive Bayes and Logistic Regression
   (each with a TF-IDF front end) on the VALIDATION split, using macro-F1.
2. Choose a confidence threshold on the validation split (safety gate).
3. Evaluate the chosen model ONCE on the TEST split and save metrics, the
   classification report, the confusion matrix and misclassified examples.
4. Save the model to models/baseline_classifier.joblib.

Run:  python src/train_baseline.py
"""
from itertools import product
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (ConfusionMatrixDisplay, accuracy_score, classification_report,
                             confusion_matrix, f1_score, precision_recall_fscore_support)
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

SEED = 42
ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "processed" / "dataset.csv"
RESULTS = ROOT / "results"
MODEL_FILE = ROOT / "models" / "baseline_classifier.joblib"

# Minimum accuracy we want on queries the system answers without asking for clarification.
# The threshold is the lowest confidence that reaches this on the validation split.
TARGET_ACCEPTED_ACCURACY = 0.90
THRESHOLDS = np.round(np.arange(0.20, 0.96, 0.05), 2)


def make_pipeline(model_name, ngram_range, stop_words, param):
    tfidf = TfidfVectorizer(ngram_range=ngram_range, stop_words=stop_words, sublinear_tf=True)
    if model_name == "naive_bayes":
        clf = MultinomialNB(alpha=param)
    elif model_name == "logistic_regression":
        clf = LogisticRegression(C=param, class_weight="balanced", max_iter=3000, random_state=SEED)
    else:
        clf = DummyClassifier(strategy="most_frequent")
    return Pipeline([("tfidf", tfidf), ("clf", clf)])


def candidate_configs():
    yield {"model": "dummy_most_frequent", "ngram_range": (1, 1), "stop_words": None, "param": None}
    for ngram, stop in product([(1, 1), (1, 2)], [None, "english"]):
        for alpha in [0.01, 0.1, 0.5, 1.0]:
            yield {"model": "naive_bayes", "ngram_range": ngram, "stop_words": stop, "param": alpha}
        for c in [0.5, 1.0, 5.0, 10.0]:
            yield {"model": "logistic_regression", "ngram_range": ngram, "stop_words": stop, "param": c}


def summary_metrics(y_true, y_pred):
    p_m, r_m, f_m, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)
    p_w, r_w, f_w, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted", zero_division=0)
    return {"n": len(y_true), "accuracy": accuracy_score(y_true, y_pred),
            "precision_macro": p_m, "recall_macro": r_m, "f1_macro": f_m,
            "precision_weighted": p_w, "recall_weighted": r_w, "f1_weighted": f_w}


def threshold_table(confidence, correct):
    rows = []
    for t in THRESHOLDS:
        accepted = confidence >= t
        rows.append({"threshold": t, "coverage": accepted.mean(),
                     "accepted_accuracy": correct[accepted].mean() if accepted.any() else np.nan})
    return pd.DataFrame(rows)


def main():
    RESULTS.mkdir(exist_ok=True)
    MODEL_FILE.parent.mkdir(exist_ok=True)
    df = pd.read_csv(DATA_FILE)
    train, val, test = (df[df["split"] == s] for s in ["train", "validation", "test"])
    print(f"train={len(train)}  validation={len(val)}  test={len(test)}")

    # 1. Model selection on the validation split
    comparison = []
    for cfg in candidate_configs():
        pipe = make_pipeline(cfg["model"], cfg["ngram_range"], cfg["stop_words"], cfg["param"])
        pipe.fit(train["text"], train["label"])
        pred = pipe.predict(val["text"])
        comparison.append({**cfg, "val_accuracy": accuracy_score(val["label"], pred),
                           "val_f1_macro": f1_score(val["label"], pred, average="macro", zero_division=0)})
    comparison = pd.DataFrame(comparison).sort_values("val_f1_macro", ascending=False)
    comparison.to_csv(RESULTS / "validation_comparison.csv", index=False)
    print("\nTop validation results:\n", comparison.head(8).to_string(index=False))
    print("\nBest per model type:\n",
          comparison.groupby("model").head(1).to_string(index=False))

    best = comparison.iloc[0].to_dict()
    best_cfg = {k: best[k] for k in ["model", "ngram_range", "stop_words", "param"]}
    best_cfg["stop_words"] = None if pd.isna(best_cfg["stop_words"]) else best_cfg["stop_words"]
    print(f"\nSelected: {best_cfg}")
    model = make_pipeline(**{"model_name": best_cfg["model"], "ngram_range": best_cfg["ngram_range"],
                             "stop_words": best_cfg["stop_words"], "param": best_cfg["param"]})
    model.fit(train["text"], train["label"])

    # 2. Confidence threshold on the validation split
    val_proba = model.predict_proba(val["text"])
    val_conf = val_proba.max(axis=1)
    val_correct = (model.classes_[val_proba.argmax(axis=1)] == val["label"].to_numpy())
    val_thr = threshold_table(val_conf, val_correct)
    val_thr.to_csv(RESULTS / "validation_thresholds.csv", index=False)
    reaching = val_thr[val_thr["accepted_accuracy"] >= TARGET_ACCEPTED_ACCURACY]
    threshold = float(reaching["threshold"].min()) if len(reaching) else float(THRESHOLDS.max())
    print(f"\nValidation threshold table:\n{val_thr.to_string(index=False)}")
    print(f"Chosen confidence threshold: {threshold}")

    # 3. One-time evaluation on the test split
    test_proba = model.predict_proba(test["text"])
    test_pred = model.classes_[test_proba.argmax(axis=1)]
    test_conf = test_proba.max(axis=1)
    y_test = test["label"].to_numpy()

    rows = [{"subset": "all_test", **summary_metrics(y_test, test_pred)}]
    for source in sorted(test["source"].unique()):
        mask = (test["source"] == source).to_numpy()
        rows.append({"subset": f"test_{source}", **summary_metrics(y_test[mask], test_pred[mask])})
    metrics = pd.DataFrame(rows)
    metrics.to_csv(RESULTS / "metrics.csv", index=False, float_format="%.4f")
    print("\nTest metrics:\n", metrics.to_string(index=False, float_format="%.4f"))

    report = classification_report(y_test, test_pred, digits=4, zero_division=0)
    with open(RESULTS / "classification_report.txt", "w", encoding="utf-8") as f:
        f.write(f"Selected model: {best_cfg}\nTest set size: {len(test)}\n\n{report}")
    print("\n", report)

    test_thr = threshold_table(test_conf, test_pred == y_test)
    at = test_thr[test_thr["threshold"] == threshold].iloc[0]
    with open(RESULTS / "threshold_on_test.txt", "w", encoding="utf-8") as f:
        f.write(f"threshold={threshold}\ncoverage={at['coverage']:.4f}\n"
                f"accepted_accuracy={at['accepted_accuracy']:.4f}\n")
    print(f"At threshold {threshold} on test: coverage={at['coverage']:.4f}, "
          f"accuracy on accepted={at['accepted_accuracy']:.4f}")

    labels = list(model.classes_)
    cm = confusion_matrix(y_test, test_pred, labels=labels)
    fig, ax = plt.subplots(figsize=(10, 8.5))
    ConfusionMatrixDisplay(cm, display_labels=labels).plot(ax=ax, cmap="Blues", xticks_rotation=45,
                                                          colorbar=False)
    ax.set_title("Baseline classifier - confusion matrix (test set, counts)")
    fig.tight_layout()
    fig.savefig(RESULTS / "confusion_matrix.png", dpi=150)
    plt.close(fig)

    errors = test.assign(predicted=test_pred, confidence=test_conf)
    errors = errors[errors["label"] != errors["predicted"]]
    errors[["id", "source", "label", "predicted", "confidence", "text"]].to_csv(
        RESULTS / "misclassified_test_examples.csv", index=False)

    # Most informative words per class (interpretability)
    vocab = np.array(model.named_steps["tfidf"].get_feature_names_out())
    clf = model.named_steps["clf"]
    weights = clf.coef_ if hasattr(clf, "coef_") else clf.feature_log_prob_
    with open(RESULTS / "top_terms_per_class.txt", "w", encoding="utf-8") as f:
        for label, w in zip(labels, weights):
            f.write(f"{label}: {', '.join(vocab[np.argsort(w)[::-1][:15]])}\n")

    # 4. Save the model bundle
    joblib.dump({"pipeline": model, "threshold": threshold, "labels": labels, "config": best_cfg,
                 "sklearn_version": sklearn.__version__}, MODEL_FILE)
    print(f"\nSaved model to {MODEL_FILE}")


if __name__ == "__main__":
    main()
