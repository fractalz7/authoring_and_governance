# Roadmap (draft)

> Working draft for the take-home. Phases, order and reasons as discussed so far; figures, if any, are illustrative.

The principle behind the order: **governed knowledge first, search right behind it, channels on top.** You cannot retrieve your way out of an unstructured pile, but search should not wait for the whole pile either: its logs tell authors what to write next.

| Phase | What ships | Why in this order | Status in this repo |
|---|---|---|---|
| **0. Ontology** | Unit types, compliance classes, topics, knowledge bases, roles, channels, Humana-speak lexicon. AI proposes a seed from the corpus; SMEs and Legal approve | Everything after it (tagging, approval gates, access scoping, query expansion) reads from it | Treated as done: `ingestion/knowledge_ontology_v1.json` |
| **1. Author and govern, one domain** | Upload → units → tags → duplicate and conflict check → human approval gates → versioned publish. Start with Pharmacy (Rx) | Legal verbatim is where inconsistency costs most; one domain proves the loop before scaling it | Built: `ingestion/`, `approvals/` |
| **2. Search on that first knowledge base** | Hybrid search (keyword + meaning-based embeddings + lexicon expansion) over **published units only**, scoped by role before retrieval, cites the unit, says "no approved answer" and logs the question to the author's gap queue. Measured on a golden set before anyone relies on it | Launches with the first governed knowledge base, not after full migration: empty searches are the authoring backlog | Next |
| **3. Drift and lifecycle** | A revised source is treated as a new upload: its units are diffed, flagged stale, and a fix is proposed for approval. Plan-year expiry | Keeps the single source correct once it exists; without it, drift comes back | Next |
| **4. Channels** | One API serving the same approved unit to advocate assist, member chat, voice bot, web and outbound. Verbatim units are returned exactly, never generated | The other AI use cases wait on grounded, citable knowledge; they plug in once phases 1–3 hold | Later |
| **5. Scale** | More domains (Insurance, then clinical with a clinical reviewer gate), bulk migration of the legacy pile, LLM splitting of unmarked documents, search analytics that surface blind spots and propose units, synonyms learned from logs | Repeats a proven loop; AI does more of the extraction as volume grows | Later |

## Production hardening (runs alongside phases 2–5)

- **State and audit:** LangGraph checkpoints move from memory to a database (Postgres); `decisions.txt` becomes an **append-only audit table**.
- **Knowledge store:** from in-memory Chroma to a persistent vector database, holding two vectors per unit: the wording-based one for duplicates and drift, a meaning-based one for search.
- **Review screen:** a real approve/reject UI for Legal and authors in place of `decide()` cells, with the diff and the list of channels each unit reaches.
- **Identity and access:** roles come from SSO groups; granting a role access to a knowledge base stays a human decision.
- **Evaluation in CI:** the golden set (and a growing set of synthetic cases) runs on every change to extraction, tagging or retrieval.

## What we chose not to build in the prototype

- **Persistent state (SQLite) in Colab:** the decision log already covers the audit need, and resuming would also require a persistent knowledge store. Moved to production hardening.
- **Autonomous multi-agent approvals (CrewAI-style):** humans own legal and clinical decisions; agents playing reviewers would undercut the approval gate. LangGraph keeps the routes fixed and the gates human.
