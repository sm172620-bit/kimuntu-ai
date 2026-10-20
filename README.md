# Kimuntu AI: Week 1 Baseline Legal Query Classifier

Riipen industry project with Kimuntu Power Inc. (course: AI and Expert Systems in Action).

> **Disclaimer:** this system supports user understanding of legal situations. It does not
> provide legal advice and does not replace a qualified legal professional.

The project classifies an English user query into one of 9 categories (8 legal areas + out-of-scope)
and returns a confidence score. It is the first component of the flow
**User Query → Text Classification → Information Retrieval → Decision Support → Recommendation → Chatbot Response**.

**Submission file:** `report/Kimuntu_AI_Week1_Report.docx` (Word), which contains all deliverables.

## Results at a glance (test set, 1,061 queries)

| Model | Accuracy | Macro-F1 | Weighted F1 |
|---|---|---|---|
| TF-IDF + Logistic Regression (selected on validation) | 0.8652 | 0.8020 | 0.8644 |

Details and limitations: [`docs/interpretation.md`](docs/interpretation.md).

## Project structure

```
├─ README.md              this file
├─ requirements.txt       pinned dependencies
├─ docs/
│  ├─ problem_scope.md          1. problem and scope statement
│  ├─ categories.md             2. classification categories
│  ├─ architecture.md/.mmd/.png 3. architecture diagram and explanation
│  ├─ interpretation.md         7. interpretation and Week 2 improvements
│  ├─ team_roles.md             proposed (random) role allocation for the group, to be confirmed
│  └─ individual_contribution.md 8. individual contribution (template, to be completed)
├─ data/
│  ├─ README.md                 4. data sources, licences, preprocessing
│  ├─ synthetic/synthetic_queries.csv   SYNTHETIC queries (AI-written, marked as such)
│  ├─ processed/dataset.csv     prepared dataset with train/validation/test split
│  └─ raw/                      downloaded data (not in Git; re-created by the script)
├─ src/
│  ├─ text_utils.py             shared text cleaning
│  ├─ prepare_data.py           download + clean + split
│  ├─ train_baseline.py         5./6. train, select, evaluate, save model
│  ├─ predict.py                predict(query) -> category + confidence
│  ├─ draw_architecture.py      draws docs/architecture.png
│  └─ build_report.py           builds the Word report
├─ notebooks/baseline_classifier.ipynb   Colab-compatible notebook (same as train_baseline.py)
├─ models/baseline_classifier.joblib     saved model + threshold
├─ results/                     metrics, classification report, confusion matrix, error analysis
└─ report/Kimuntu_AI_Week1_Report.docx   Word submission
```

## How to run locally (Windows, Python 3.14)

```bash
python -m venv .venv
.venv\Scripts\activate            # Git Bash: source .venv/Scripts/activate
pip install -r requirements.txt

python src/prepare_data.py        # downloads Law Stack Exchange (~106 MB) and builds data/processed/dataset.csv
python src/train_baseline.py      # trains, evaluates, writes results/ and models/
python src/predict.py "My landlord has refused to return my security deposit."
python src/draw_architecture.py   # redraws docs/architecture.png
python src/build_report.py        # rebuilds report/Kimuntu_AI_Week1_Report.docx
```

`data/processed/dataset.csv` is already committed, so `prepare_data.py` is only needed to rebuild it.

### Using the classifier from other code

```python
import sys; sys.path.append("src")
from predict import predict
predict("My employer has not paid my salary")
# {'category': ..., 'confidence': ..., 'top_3': [...], 'needs_clarification': ..., 'threshold': 0.35}
```

`needs_clarification` is `True` when the query is out of scope or the confidence is below the
threshold. The chatbot should then ask the user to rephrase or refer them to a professional.

## How to run on Google Colab

1. Open <https://colab.research.google.com> → *File → Upload notebook* → choose
   `notebooks/baseline_classifier.ipynb`.
2. *Runtime → Run all*. When asked, upload `data/processed/dataset.csv`.

Colab already includes scikit-learn, pandas, numpy, matplotlib and joblib, but its versions may differ
from `requirements.txt`, which can cause very small differences in the numbers. For identical results,
first run `!pip install scikit-learn==1.9.1 pandas==3.0.6 numpy==2.5.4` in a cell, *if* Colab's Python
version supports these versions.

## Reproducibility

- Random seed 42 for the data split and the model.
- The Law Stack Exchange download is pinned to commit `ab2dbaad9a71b6550316994c8fcd69f24f7f16e6`.
- The test set is used once, after model selection on the validation set.
- `notebooks/baseline_classifier.ipynb` was checked to give the same numbers as `src/train_baseline.py`.

## Data sources and licences

- **Law Stack Exchange dataset**: Moslem, Y. (2023), Hugging Face,
  <https://huggingface.co/datasets/ymoslem/Law-StackExchange>, DOI 10.57967/hf/4792. Licence CC BY-SA 4.0.
  The derived `data/processed/dataset.csv` is shared under CC BY-SA 4.0.
- **Synthetic queries**: written for this project by an AI assistant (Claude). Not real user data.

See [`data/README.md`](data/README.md) for full details.

## Use of AI assistance

This repository was developed with an AI coding assistant (Claude, by Anthropic). Commits made with
its help carry a `Co-Authored-By: Claude` line.
