# Data: Description and Preprocessing

The company dataset promised by Kimuntu Power Inc. is not yet available. The baseline therefore uses a
combination of one **public** dataset and one **synthetic** dataset. Every row records its origin
in the `source` column, so results can be checked per source.

## Files

| File | What it is | In Git? |
|---|---|---|
| `raw/law-stackexchange-questions-answers.json` | Original Law Stack Exchange download (106,154,624 bytes) | No: re-created by `src/prepare_data.py` |
| `synthetic/synthetic_queries.csv` | 450 **synthetic** queries (`text`, `label`) | Yes |
| `processed/dataset.csv` | Final prepared dataset: `id`, `text`, `label`, `source`, `split` (7,071 rows) | Yes |

## Source 1: Law Stack Exchange (public, real questions)

- **Dataset:** *Law-StackExchange Dataset*, Yasmin Moslem (2023), Hugging Face.
  <https://huggingface.co/datasets/ymoslem/Law-StackExchange>, DOI 10.57967/hf/4792
- **Version used:** repository commit `ab2dbaad9a71b6550316994c8fcd69f24f7f16e6` (pinned in the script).
- **Content:** 24,370 questions (and answers) from the Law Stack Exchange website, collected up to
  14 August 2023. Each question has a title, body (HTML) and user-assigned tags. Only titles, bodies
  and tags are used; answers are ignored.
- **Licence:** CC BY-SA 4.0 (dataset card). Individual posts are CC BY-SA 3.0 or 4.0 under Stack
  Exchange's content licence. `processed/dataset.csv` contains text derived from these posts and is
  therefore shared under **CC BY-SA 4.0** with attribution to the dataset author and Law Stack Exchange
  contributors.
- **Why chosen:** real questions from people in many countries (international), a clear open licence,
  and tags that can be mapped to our categories.

### How tags were mapped to categories

A question is kept only if (a) none of its tags is an out-of-taxonomy domain, and (b) its remaining
tags map to **exactly one** of our categories. Questions whose tags point to two categories (e.g.
`lease` + `real-estate`) are dropped because their label would be ambiguous. Tags were chosen
after counting tag frequencies in the downloaded file. Only tags that exist in the data are used.

| Category | Law Stack Exchange tags used |
|---|---|
| `housing_tenancy` | landlord, tenant, rental-property, lease, eviction, residential-lease, rent, tenancy-rules, tenancy |
| `employment_labour` | employment, labor-law, employer, employee, workplace, unemployment, salary |
| `business_commercial` | business, corporate-law, limited-liability-company, partnership, shareholders, incorporation, non-profit |
| `land_property` | real-estate, real-property, easement, zoning, homeownership, hoa |
| `family` | family-law, divorce, marriage, child-support, parental-rights, adoption |
| `succession_inheritance` | inheritance, wills, estate-planning, probate, executor, trusts-and-estates |
| `criminal` | criminal-law, police, arrest, criminal-procedure, theft, assault, sentencing, murder, sexual-assault, rape, bail |
| `consumer_contract` | consumer-protection, contract-law, debt, warranties, warranty, refund, breach-of-contract |

- **Ambiguous tags deliberately not used:** `property` (could be intellectual property), `ownership`,
  `fraud` (criminal or civil), `death`, `children`, `trespass`.
- **Excluded out-of-taxonomy tags** (question dropped if present): copyright, intellectual-property,
  trademark, patents, fair-use, dmca, creative-commons, gdpr, privacy, data-protection, software,
  open-source-software, licensing, eula, gpl, terms-of-service, internet, tax-law, immigration,
  constitutional-law, us-constitution.
- **Result:** 6,621 of 24,370 questions kept.

## Source 2: Synthetic Uganda-context queries (SYNTHETIC)

> **This data is synthetic.** It was written for this project by an AI assistant (Claude, by Anthropic).
> It is not real user data and does not describe real people or cases.

- **How it was generated:** 50 short queries per category (450 in total) were written by hand by the AI
  assistant in one pass: one query per line, in plain everyday English, some informal or
  lower-case, many with Ugandan context (place names such as Kampala, Mbarara, Wakiso; terms such as
  *kibanja*, *mailo land*, *boda boda*, *NSSF*, *URSB*, *SACCO*, shillings). No templates or automatic
  generation were used. Each query was assigned its label by the author following the labelling rules
  in `docs/categories.md`.
- **Why it is needed:**
  1. it is the **only** source for `other_out_of_scope` (Law Stack Exchange contains only legal questions);
  2. it gives short, chat-style queries like those a chatbot will receive;
  3. no public labelled dataset of Ugandan legal queries could be found.
- **Known bias:** a single author's style, cleaner than real user text, and much shorter than Law Stack
  Exchange posts (mean 11.7 words vs 148.5 words). See `docs/interpretation.md` for the effect on results.
- The legal statements implied by the queries were **not** verified, and they do not need to be: the
  queries are only examples of *questions*, used to teach the classifier which category a question
  belongs to. No legal facts are taken from them.

## Preprocessing (`src/prepare_data.py`)

| Step | What | Why |
|---|---|---|
| 1 | Combine Law Stack Exchange title + body | The title alone is often too short to show the legal area |
| 2 | Remove HTML tags, decode HTML entities, remove URLs | Law Stack Exchange bodies are HTML; tags and links are not legal content |
| 3 | Lowercase and collapse whitespace | "Landlord" and "landlord" should be the same word |
| 4 | Keep only the first 300 words | Very long posts would dominate the word statistics; the topic is normally clear early on |
| 5 | Drop empty texts | None needed to be dropped in the final run |
| 6 | Remove exact duplicate texts | Prevents the same text appearing in train and test (leakage); 0 duplicates found |
| 7 | Stratified split 70 / 15 / 15 (train / validation / test), `random_state=42`, stratified on label + source | Every split has the same mix of categories and sources; seed makes it reproducible |
| 8 | Assert that no text occurs in two splits | Leakage check |

Stop-word removal and n-grams are **not** done here. They are settings of the TF-IDF vectoriser, tested
on the validation set in `src/train_baseline.py`.

The same cleaning function (`src/text_utils.py`) is applied to new queries at prediction time.

## Final dataset (`processed/dataset.csv`)

| Category | LSE train | LSE val | LSE test | Synthetic train | Synthetic val | Synthetic test | Total |
|---|---|---|---|---|---|---|---|
| business_commercial | 356 | 77 | 76 | 35 | 7 | 8 | 559 |
| consumer_contract | 1057 | 227 | 226 | 35 | 7 | 8 | 1560 |
| criminal | 1573 | 337 | 337 | 35 | 7 | 8 | 2297 |
| employment_labour | 445 | 95 | 95 | 35 | 8 | 7 | 685 |
| family | 279 | 60 | 60 | 35 | 7 | 8 | 449 |
| housing_tenancy | 521 | 112 | 112 | 35 | 7 | 8 | 795 |
| land_property | 220 | 47 | 47 | 35 | 8 | 7 | 364 |
| other_out_of_scope | 0 | 0 | 0 | 35 | 8 | 7 | 50 |
| succession_inheritance | 183 | 40 | 39 | 35 | 7 | 8 | 312 |
| **Total** | **4634** | **995** | **992** | **315** | **66** | **69** | **7071** |

The classes are clearly **imbalanced**: `criminal` has 2,297 examples while `other_out_of_scope` has 50.

## Re-creating the data

```bash
python src/prepare_data.py
```

This downloads the pinned Law Stack Exchange file (if not already in `data/raw/`) and rebuilds
`processed/dataset.csv`. With the same file and seed the output is identical.
