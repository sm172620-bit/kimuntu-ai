# Problem and Scope Statement

**Project:** Kimuntu AI (Riipen industry project, partner: Kimuntu Power Inc.)
**Course:** AI and Expert Systems in Action
**Week 1 focus:** system design and baseline legal text classifier

> **Disclaimer:** Kimuntu AI is designed to support a user's *understanding* of a legal
> situation. It does not give legal advice and does not replace a qualified legal professional.

## The problem

People who face an everyday legal problem, such as a landlord keeping a deposit, an employer
not paying wages, or uncertainty about registering a business, often do not know which area of law
their problem belongs to or where to go for help. Kimuntu AI aims to help them by understanding the
question, retrieving approved information, structuring the relevant considerations, recommending
resources or next steps, and presenting this through a chatbot.

Before the system can do any of that, it must first **understand what kind of legal problem the
user is describing**. A query about a security deposit must be routed to housing and tenancy
material, not to employment or criminal material. If the query is not a legal question at all, or
the system is unsure, it must say so instead of answering confidently.

## What Week 1 delivers

1. A set of legal query categories that the system should recognise (`docs/categories.md`).
2. A system architecture showing how the text classifier, legal decision support system,
   recommendation system and chatbot work together (`docs/architecture.md`).
3. A prepared dataset, built while company data is awaited (`data/`).
4. A baseline text classifier (TF-IDF with Logistic Regression / Naive Bayes) that returns a category
   and a confidence score for a user query (`notebooks/`, `src/`, `models/`).
5. Evaluation results and an interpretation with proposed Week 2 improvements (`results/`,
   `docs/interpretation.md`).

## Scope

| In scope (Week 1) | Out of scope (later weeks) |
|---|---|
| English-language user queries | Other languages / translation |
| Uganda-context and international queries | Jurisdiction-specific legal answers |
| Single-label, domain-level classification into 9 categories (8 legal + out-of-scope) | Issue-level or intent-level labels, multi-label classification |
| Confidence score and a "needs clarification" flag | Retrieval, decision support, recommendation and chatbot implementation |
| Interpretable scikit-learn baseline | Large language models, deep learning, embeddings |
| Saved model with a callable `predict()` function | FastAPI/Flask service, front end, database, payment integration |

## Users and stakeholders

- **End users:** members of the public with an everyday legal question.
- **Kimuntu Power Inc.:** industry partner, owner of the platform and of future company data.
- **Project team and lecturer:** build and assess the prototype.

## Key assumptions (to be confirmed with Kimuntu)

- The jurisdiction focus is **Uganda plus international** queries, as agreed by the team.
  Kimuntu has not yet confirmed jurisdictions or priority categories.
- Kimuntu will provide data later. Until then, a combination of a public dataset
  (Law Stack Exchange) and a clearly labelled **synthetic** dataset is used.
- The categories are a team proposal and may be revised once Kimuntu's priorities are known.
