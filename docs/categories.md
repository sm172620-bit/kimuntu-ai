# Proposed Legal Query Categories

The classifier assigns **one** category to each user query. There are **8 legal categories** and
**1 out-of-scope category**. The categories are at the level of *legal domain*, because:

- the lecturer note's example ("My landlord has refused to return my security deposit" → *housing
  law, tenancy dispute, legal guidance*) mixes domain, issue and intent. Picking a single level keeps
  labelling consistent and the model explainable;
- domain labels are what the later components need first: retrieval needs to know *which body of
  law* to search, and recommendation needs to know *which family of resources* to offer;
- issue- or intent-level labels (e.g. "deposit dispute", "wants a template letter") can be added in a
  later week as a second layer once Kimuntu's priorities and data are known.

> These categories are a team proposal. Kimuntu Power Inc. has not yet confirmed jurisdictions or
> priority categories. The example queries below are illustrative and were written for this
> project with AI assistance. They are not real user data.

| # | Label | Definition | Example queries | Basis |
|---|---|---|---|---|
| 1 | `housing_tenancy` | Renting a home or room: landlord–tenant relations, rent, deposits, repairs, eviction. | "My landlord has refused to return my security deposit." / "The landlord wants to evict me without notice." | Lecturer note example (security deposit) |
| 2 | `employment_labour` | Work relationships: wages, dismissal, employment contracts, leave, workplace treatment. | "My employer has not paid my salary for three months." / "I was dismissed without any reason. What can I do?" | Lecturer note examples (employment termination, unpaid wages) |
| 3 | `business_commercial` | Starting, registering or running a business: registration, licences, partnerships, company matters. | "How do I register a small business in Kampala?" / "My business partner is withdrawing money without telling me." | Lecturer note example (business registration) |
| 4 | `land_property` | Owning, buying, selling or using land and buildings: titles, boundaries, land sales. | "A neighbour has moved the boundary marks onto my land." / "How can I check that a land title is genuine before buying?" | Team addition: land is a frequent source of disputes in Uganda. Kept separate from tenancy (owning vs renting). |
| 5 | `family` | Marriage, separation and divorce, child custody, child maintenance, domestic relations. | "My husband refuses to support our children after we separated." / "What is the process for getting a divorce?" | Team addition: common legal-aid area |
| 6 | `succession_inheritance` | Wills, inheritance and administering the estate of someone who has died. | "My father died without a will. How is his property shared?" / "My uncle took over my late mother's house." | Team addition: common in Uganda; deliberately tests confusion with land and family |
| 7 | `criminal` | Arrest, police, bail, criminal charges, or being the victim of a crime. | "The police arrested my brother and he has not been charged." / "Someone stole my phone and threatened me." | Team addition: high-risk area that will always require escalation to a professional |
| 8 | `consumer_contract` | Buying goods and services, faulty products, debts, loans and general contracts between individuals. | "The shop refused to refund a phone that stopped working after a week." / "A friend borrowed money and refuses to pay it back." | Team addition: common everyday category |
| 9 | `other_out_of_scope` | Not a legal question, or a request the system should not handle (e.g. general chat, medical, cooking). | "What is the weather in Entebbe tomorrow?" / "Give me a recipe for rolex (the Ugandan chapati-and-egg snack)." | Lecturer note: the system must recognise situations it cannot safely answer |

## How the categories connect to later components

| Category | Information retrieval (approved sources only) | Decision support | Recommendation |
|---|---|---|---|
| `housing_tenancy` | Tenancy material for the user's jurisdiction | Structure: type of tenancy, notice, deposit, documents held | Tenancy resources, template letters, mediation/legal-aid contacts |
| `employment_labour` | Employment/labour material | Structure: contract type, length of service, reason for dismissal, unpaid amounts | Labour office or complaint guidance, documents to gather |
| `business_commercial` | Business registration and commercial material | Structure: business type, registration stage | Registration services, checklists, Kimuntu business resources |
| `land_property` | Land material | Structure: type of ownership, documents, nature of dispute | Land-office resources; referral when ownership is disputed |
| `family` | Family material | Structure: relationship, children involved, safety concerns | Family / legal-aid referral; urgent help if safety risk |
| `succession_inheritance` | Succession material | Structure: will or no will, relationship to the deceased | Estate guidance, referral to a professional |
| `criminal` | Only general information | **Always escalates** to a professional | Legal-aid / advocate referral, emergency contacts |
| `consumer_contract` | Consumer and contract material | Structure: what was agreed, evidence, amount | Complaint routes, demand-letter templates |
| `other_out_of_scope` | None | None | Chatbot explains the system's scope or asks the user to rephrase |

A query predicted with **low confidence** (below a threshold tuned on validation data) is treated
like an uncertain case: the chatbot asks a clarifying question or suggests a professional instead of
proceeding with a possibly wrong category.

## Labelling rules

- One label per query: the **main** legal problem the user wants help with.
- Renting → `housing_tenancy`. Owning or buying → `land_property`.
- Property of someone who has died → `succession_inheritance`, even if it is land.
- Money owed under an employment relationship → `employment_labour`. Money owed by anyone else →
  `consumer_contract`.
- Police involvement or a crime → `criminal`.
