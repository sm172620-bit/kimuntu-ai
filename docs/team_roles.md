# Proposed Team Role Allocation (to be confirmed by the group)

> **Status: PROPOSAL.** These roles were assigned **at random** so the group has a starting point.
> They describe **planned** responsibilities for the 4-week project, not work already done.
> Each member should confirm, swap or change their role in a group meeting. Each member must still
> write their **own** contribution statement describing what they actually did.

**How the roles were assigned:** the 13 roles below were matched to the 13 members with a seeded
random shuffle (`random.Random(2026).shuffle`, Python), so the allocation is fair and reproducible.

The roles cover the four workstreams in the lecturer note (text classification, legal decision
support, recommendation system, chatbot) plus the shared work every project needs.

| # | Proposed role | Workstream | Planned responsibilities | Assigned to |
|---|---|---|---|---|
| 1 | Project coordinator and employer liaison | All | Run group meetings, track the plan, lead communication with Kimuntu Power Inc. and the lecturer, work through the employer discussion checklist | KAZIBWE BENJAMIN |
| 2 | Requirements and documentation lead | All | Record agreed requirements and decisions, maintain the docs and the Word report, keep the README current | Baboucarr A Bobb |
| 3 | Data lead | Text classification | Agree data access with Kimuntu, check dataset licences, maintain `data/README.md` | CHOL MANGONG AJAL BOL |
| 4 | Data preparation and labelling | Text classification | Review the tag mapping and labelling rules, review and extend the synthetic queries, fix label noise | BIYINZIKA EMMANUEL ONYUTA |
| 5 | Text classifier lead | Text classification | Own the training script and notebook, run Week 2 model improvements | Henok Tesfahiwet Lbab Fidel |
| 6 | Model evaluation and error analysis | Text classification | Own metrics, confusion matrix and failure analysis; tune the confidence threshold | TUGUME ANDREW |
| 7 | Legal decision support lead | Decision support | Design the structured workflow (issue, factors, next steps) and the escalation rules | NAZIF SABO DANLADI |
| 8 | Legal knowledge sources and retrieval | Decision support | Identify approved sources (e.g. ULII, pending approval), build and evaluate retrieval, keep sources traceable | KAWUMA MICHAEL |
| 9 | Recommendation system lead | Recommendation | Define what is recommended per category, build the rule-based recommender | ATUHAIRE LYNNET |
| 10 | Recommendation relevance testing | Recommendation | Write test scenarios and rate the relevance of recommendations | NAMUSANA REBECCA |
| 11 | Chatbot lead | Chatbot | Build the conversation flow that presents the outputs of the other components | NASSEJJE RACHEAL |
| 12 | Integration and API | Chatbot / all | Wrap `predict()` and the other components in one API (FastAPI or Flask), connect them end to end | Mustapha suleiman Ali |
| 13 | Safety, testing and quality assurance | All | Disclaimers, refusal/clarification/referral cases, end-to-end test scenarios, final demo checklist | TWIJUKYE DISMAS |
