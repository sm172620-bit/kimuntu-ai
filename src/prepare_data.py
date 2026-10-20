"""Build data/processed/dataset.csv from two sources.

1. Law Stack Exchange (real, international questions), CC BY-SA 4.0
   https://huggingface.co/datasets/ymoslem/Law-StackExchange  (pinned commit below)
   Each question has several user-assigned tags. A question is kept only when its tags
   map to exactly ONE of our categories, so its label is unambiguous.
2. data/synthetic/synthetic_queries.csv: SYNTHETIC Uganda-context queries written
   for this project by an AI assistant (Claude) (see data/README.md).

Steps: download -> map tags to labels -> clean text -> drop short texts ->
remove duplicates -> stratified 70/15/15 train/validation/test split (seed 42).

Run:  python src/prepare_data.py
"""
import json
import urllib.request
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from text_utils import clean_text

SEED = 42
ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
RAW_FILE = RAW_DIR / "law-stackexchange-questions-answers.json"
SYNTHETIC_FILE = ROOT / "data" / "synthetic" / "synthetic_queries.csv"
OUT_FILE = ROOT / "data" / "processed" / "dataset.csv"

LSE_REVISION = "ab2dbaad9a71b6550316994c8fcd69f24f7f16e6"
LSE_URL = ("https://huggingface.co/datasets/ymoslem/Law-StackExchange/resolve/"
           f"{LSE_REVISION}/law-stackexchange-questions-answers.json")

# Law Stack Exchange tag -> our category. Only tags that exist in the dataset and clearly
# belong to one category are used (ambiguous tags such as "property", "ownership", "fraud",
# "death", "children" and "trespass" are deliberately left out). See data/README.md.
TAG_MAP = {
    "housing_tenancy": ["landlord", "tenant", "rental-property", "lease", "eviction",
                        "residential-lease", "rent", "tenancy-rules", "tenancy"],
    "employment_labour": ["employment", "labor-law", "employer", "employee", "workplace",
                          "unemployment", "salary"],
    "business_commercial": ["business", "corporate-law", "limited-liability-company", "partnership",
                            "shareholders", "incorporation", "non-profit"],
    "land_property": ["real-estate", "real-property", "easement", "zoning", "homeownership", "hoa"],
    "family": ["family-law", "divorce", "marriage", "child-support", "parental-rights", "adoption"],
    "succession_inheritance": ["inheritance", "wills", "estate-planning", "probate", "executor",
                               "trusts-and-estates"],
    "criminal": ["criminal-law", "police", "arrest", "criminal-procedure", "theft", "assault",
                 "sentencing", "murder", "sexual-assault", "rape", "bail"],
    "consumer_contract": ["consumer-protection", "contract-law", "debt", "warranties", "warranty",
                          "refund", "breach-of-contract"],
}
TAG_TO_LABEL = {tag: label for label, tags in TAG_MAP.items() for tag in tags}

# Questions carrying any of these tags are about legal areas outside our 8 categories
# (e.g. a "contract-law" question about software licensing), so they are dropped to keep labels clean.
EXCLUDE_TAGS = {"copyright", "intellectual-property", "trademark", "patents", "fair-use", "dmca",
                "creative-commons", "gdpr", "privacy", "data-protection", "software",
                "open-source-software", "licensing", "eula", "gpl", "terms-of-service", "internet",
                "tax-law", "immigration", "constitutional-law", "us-constitution"}

MIN_WORDS = 1          # drop texts that are empty after cleaning
MAX_WORDS = 300        # Law Stack Exchange posts are long; keep the first 300 words


def download_lse():
    if RAW_FILE.exists():
        return
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {LSE_URL}")
    urllib.request.urlretrieve(LSE_URL, RAW_FILE)


def load_lse() -> pd.DataFrame:
    with open(RAW_FILE, encoding="utf-8") as f:
        records = json.load(f)
    rows = []
    for r in records:
        if EXCLUDE_TAGS.intersection(r["tags"]):
            continue
        labels = {TAG_TO_LABEL[t] for t in r["tags"] if t in TAG_TO_LABEL}
        if len(labels) != 1:          # no mapped tag, or tags point to several categories
            continue
        rows.append({
            "id": f"lse_{r['question_id']}",
            "text": f"{r['question_title']} {r['question_body']}",
            "label": labels.pop(),
            "source": "law_stackexchange",
        })
    print(f"Law Stack Exchange: {len(records)} questions, {len(rows)} kept "
          "(exactly one mapped category, no out-of-taxonomy tag)")
    return pd.DataFrame(rows)


def load_synthetic() -> pd.DataFrame:
    df = pd.read_csv(SYNTHETIC_FILE)
    df["id"] = [f"syn_{i:04d}" for i in range(len(df))]
    df["source"] = "synthetic"
    print(f"Synthetic: {len(df)} queries")
    return df[["id", "text", "label", "source"]]


def main():
    download_lse()
    df = pd.concat([load_lse(), load_synthetic()], ignore_index=True)

    df["text"] = df["text"].map(clean_text).map(lambda t: " ".join(t.split()[:MAX_WORDS]))
    n_words = df["text"].str.split().str.len()
    print(f"Dropping {(n_words < MIN_WORDS).sum()} texts shorter than {MIN_WORDS} words")
    df = df[n_words >= MIN_WORDS]

    before = len(df)
    df = df.drop_duplicates(subset="text").reset_index(drop=True)
    print(f"Dropping {before - len(df)} duplicate texts")

    # Stratify on label + source so every split has each category from each source.
    strata = df["label"] + "|" + df["source"]
    train, rest = train_test_split(df, test_size=0.30, stratify=strata, random_state=SEED)
    val, test = train_test_split(rest, test_size=0.50, stratify=strata[rest.index], random_state=SEED)
    df["split"] = "train"
    df.loc[val.index, "split"] = "validation"
    df.loc[test.index, "split"] = "test"

    # Leakage check: no text may appear in more than one split.
    assert df.groupby("text")["split"].nunique().max() == 1

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FILE, index=False)
    print(f"Saved {len(df)} rows to {OUT_FILE}")
    print(pd.crosstab(df["label"], [df["source"], df["split"]], margins=True).to_string())


if __name__ == "__main__":
    main()
