# authoring_and_governance

Prototype work for a Knowledge & Search platform: authoring, governance and ingestion of knowledge units, so every channel and every search gives the same correct, cited, current answer.

> Illustrative take-home demo. Made-up data only.

## Contents

- [`ingestion/`](ingestion/): author upload → unit extraction → ontology tagging → duplicate and conflict check → routing to Legal or the author. Includes the notebook, test documents, ontology, and supporting docs.
- [`docs/overview.html`](docs/overview.html): the proposal as an interactive page (tabs for overview, journey, current and future state, ontology, proof of concept, roadmap, responsible AI, artifacts). Open it in a browser.
- [`ROADMAP.md`](ROADMAP.md): phased plan, why that order, and what moves to production hardening.
- [`approvals/`](approvals/): a LangGraph workflow that takes each finding through human approval gates (Legal or author, with a role check), publishes approved changes to Chroma as new units or versions, and keeps an audit trail.
