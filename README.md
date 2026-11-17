# authoring_and_governance

Prototype work for a Knowledge & Search platform: authoring, governance and ingestion of knowledge units, so every channel and every search gives the same correct, cited, current answer.

> Illustrative take-home demo. Made-up data only.

## Contents

- [`ingestion/`](ingestion/): author upload → unit extraction → ontology tagging → duplicate and conflict check → routing to Legal or the author. Includes the notebook, test documents, ontology, and supporting docs.
- [`approvals/`](approvals/): a LangGraph workflow that takes each finding through human approval gates (Legal or author, with a role check), publishes approved changes to Chroma as new units or versions, and keeps an audit trail.
