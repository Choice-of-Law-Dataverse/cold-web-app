---
title: Open Data — CoLD
---

# Legal Data and the FAIR Principles

*Synthesis of an interview conducted and written by **Claire Hoffmann**.*

---

## 1. Context and background

The Choice of Law Dataverse (CoLD) began as a vague mandate: produce a database connected to a research book. Turning that into a clear vision for the platform took roughly three years, against persistent institutional resistance and with almost no data management training available in legal research.

**What counts as legal data.** In the CoLD framework, legal data means source-level data points that ground legal analysis, rather than scholarly interpretations of them: legislation at all levels (down to specific provisions), court decisions (official document plus analysis), arbitral awards and rules, and legal literature. Legal data sits awkwardly between the quantitative and the qualitative — and legal researchers do not spontaneously recognise what they handle as "data" at all.

## 2. Adoption of the FAIR principles

FAIR is explicitly integrated into CoLD, but its adoption was organic and self-initiated. The trigger was the SNSF data management plan requirement. Before that, the project had no DMP, on the assumption that public legal data needed no formal governance; the prevailing bias treated DMPs as instruments of the empirical sciences.

Brandão de Oliveira frames this as a structural problem. Researchers face compliance pressure without training, tools, or models to work from — she found virtually no usable DMP examples for legal science. FAIR ended up serving as the only available framework for articulating CoLD's data structure in a principled way.

## 3. Findable

**Standards.** CoLD runs primarily on internal rules, developed collaboratively with an interdisciplinary team that included non-legal data specialists. That collaboration was essential to break out of the legal researcher's habit of treating jurisdictional variation as an obstacle to systematisation. No formal international standard governs the citation or structuring of legal data across jurisdictions; domestic standards are respected where possible as a layer of specificity, which requires constant compromise between uniformity and contextual fidelity.

An early obstacle was the complete absence of metadata awareness among legal researchers.

**Barriers to findability:**

- **Copyright** — highly ambiguous, particularly across jurisdictions. Whether fair use (a US doctrine) applies in Switzerland is uncertain, and personal data embedded in court decisions raises further questions. Common law jurisdictions amplify these concerns considerably.
- **Language** — a structural barrier for any multi-jurisdictional database.
- **Persistent identifiers** — whether individual data points should carry DOIs remains unresolved. The interim solution: the full dataset deposited in the Swiss federal repository (SWISSUbase) carries a DOI; individual entries do not.

## 4. Accessible

**Access pathways.** CoLD offers three: a web interface (the primary route, designed for legal practitioners), a public API (available, though unlikely to be used by practitioners), and downloadable data via the SWISSUbase repository. Individual entries allow export of bibliographic references (BibTeX for Zotero, for instance) and PDF download where available.

**Barriers to accessibility:**

- **Knowledge gap** — researchers do not know what making data accessible actually requires, which tools to use, or what qualifies as an open access repository under funder criteria.
- **Cultural barrier** — in legal science, the only recognised output is a publication. Research data is not seen as a legitimate academic product worth making accessible.
- **Philosophical resistance** — many researchers question the value of releasing source data at all, and some collect data informally, including in paper archives, with no intention of sharing it.
- **Infrastructure** — building an API required external technical support; without it, no API would exist. Institutional support was minimal.
- **Digitisation gap** — a substantial portion of legal data older than twenty years exists only on paper.
- **Ambiguity of open science criteria** — after five years of engagement with these questions, Brandão de Oliveira remains uncertain whether specific deposits meet SNSF's open access criteria. She considers this alarming: less-engaged researchers have no chance of navigating it correctly.

## 5. Interoperable

**Technical standards.** CoLD follows general web and platform standards, but from a legal data perspective interoperability is understood primarily as methodological consistency: an abbreviations guide, stable data schemas, and transparent linkage logic, so that another team could take the dataset and apply it elsewhere. The vocabulary and data mapping are documented internally but not formally aligned with external ontologies.

**Internal connections between source types.** Cross-referencing between decisions and legislation is done manually — when a decision cites a provision, researchers establish that link during data entry. Thematic organisation is the main connective structure: decisions, legislation, and literature sharing a theme are grouped together. This is acknowledged as rudimentary.

**International interoperability.** Endorsed without reservation as a principle: a unified platform for private international law across jurisdictions is described as her utopia. Implementation is another matter — it would require interdisciplinary teams, substantial resources, and cross-institutional coordination beyond what any one person can mobilise.

## 6. Reusable

**Quality assurance.** Reliability begins at collection, requires trained researchers for analysis and entry, and demands centralised review — a single person or a peer-review structure checking entries. This is time-consuming and imperfect; individual researcher bias survives even codified rules. Not optimal, but centralised quality control remains the only workable approach.

**AI and emerging technologies:**

- **Cannibalisation.** Open, reliable, human-curated data like CoLD's is being ingested by commercial AI tools that monetise it without credit or compensation. Troubling — though still preferable to a web dominated by synthetic data.
- **Human-curated ground truth.** In a legal environment where much web data is now synthetic, well-structured and human-verified datasets retain real value. AI output revised by a human is acceptable; AI output used unchecked is not.
- **Effort-to-value ratio.** CoLD spent two years building an LLM-based application for its own data with limited success. Setup costs for AI processing of legal data are extremely high, and reliable results are not guaranteed.
- **Data governance risks.** AI tools processing sensitive legal data raise unresolved questions of ownership, secondary use, and liability — questions lawyers should be engaging with far more actively.
- **Future landscape.** Legal databases are converging on AI-mediated query interfaces and away from Google-style search. This could improve efficiency dramatically, but risks uncritical acceptance of generated results. The ideal is AI genuinely tailored to domain needs, with reliable and transparent outputs.

## 7. Governance, priorities, and the future

**Priority under real constraints.** Accessibility should come first for the legal data ecosystem; that alone would amount to a revolution in current practice. With unlimited resources, interoperability would be the harder and more ambitious goal.

**Vision.** An integrated, stable, sustainably curated platform for private international law: one repository, all jurisdictions, consistent methodology, continuously updated, with FAIR embedded by design in the architecture.

**Three improvements for legal data quality and accessibility:**

1. **Better guidelines** — clearer, simpler, more actionable parameters for what "open" and "accessible" mean concretely in legal research.
2. **Incentive structures** — open data carries no reputational benefit comparable to a monograph. That cultural equation has to change; funder mandates alone are insufficient. The cost of open access publishing through commercial publishers is outrageous, particularly for researchers outside wealthy institutions.
3. **Methodology and professionalisation** — standardised metadata practices, machine-readable formats, and above all institutional data professionals embedded in research environments: either a dedicated data officer managing deposits across projects, or a binding SNSF rule making this mandatory. Leaving the burden with individual researchers means fewer than 10% will comply. Interdisciplinarity between legal scholars, data scientists, and librarians is essential — and currently absent.

---

## Further reading

This synthesis was prepared as an annex to Claire Hoffmann's master's thesis, which we recommend reading in full:

> Claire Hoffmann, *De l'arrêt à la donnée : pratiques et recommandations pour une application des principes FAIR aux données juridiques en Suisse*, Master's thesis, University of Fribourg, 2026.

It is, to our knowledge, the first sustained treatment of what the FAIR principles concretely require of legal data in Switzerland — and it asks the question from the right end: not what open science expects of law in the abstract, but what actually happens when a court decision is turned into a data point.