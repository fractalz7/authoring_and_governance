# Ingestion: author upload, tagging, and conflict check

> Illustrative demo for a take-home exercise. All documents, figures, names and approvals are made up.

What happens when a Knowledge Ops author uploads documents: each document is split into knowledge units, every unit is tagged against an ontology, and new units are compared with the approved ones already in a Chroma store. Findings are sorted into exact duplicate, legal wording differs, same meaning, variant, contradiction, stale or new, and routed to the right person. Legal wording is never resolved by AI.

## Files

| File | What it is |
|---|---|
| `ingestion_book.ipynb` | The demo notebook. Saved with outputs, so it reads without running |
| `RX-EDU-SCRIPT_v3.2.md` | Test doc 1: current inbound Rx education script (the approved baseline) |
| `PHARM-OUTREACH-SCRIPT_v1.7.md` | Test doc 2: older outbound script from another team, with planted duplicates and conflicts |
| `knowledge_ontology_v1.json` | The ontology (Phase 0, treated as done): classes, relations, keywords, access and approval rules, lexicon |
| `ontology_graph.html` / `ontology_graph.png` | The ontology graph with definitions, for documentation |
| `embedding_comparison.xlsx` | Wording-based vs neural embeddings: example pairs and a side-by-side of the two approaches |
| `LLM_USAGE.md` | Where an LLM is used today, where a real deployment would need one, and where it never should be |
| `build_notebook.py` | Regenerates the notebook (`python3 build_notebook.py .`) |

## Run it

**Locally:** `pip install chromadb numpy` (plus `anthropic` to turn Claude on), then open the notebook from this folder and run all cells.

**Colab:** upload the notebook, then upload the two `.md` docs and the `.json` file to the Files panel (or let the first cell prompt you). Runtime → Run all. Optional: add `ANTHROPIC_API_KEY` under Secrets.

## What the run finds (offline mode)

- 2 exact duplicates (e.g. identity verification)
- 3 legal wording differences (pricing disclaimer, recording disclosure, closing), routed to Legal
- 1 contradiction (mail-order delivery time and supply)
- 1 stale unit ("donut hole" / coverage gap)
- 4 variants (tier copays by plan year; opening, purpose and disposition codes by channel)
- 8 new units (voicemail, do-not-call, billing, and others)

One planted conflict (preferred-pharmacy copays) is missed offline; Claude catches claim-level contradictions. See `LLM_USAGE.md`.

## Design notes

- The **unit**, not the document, is what gets tagged, approved, versioned and served.
- **Chroma holds published units only.** Drafts are compared, never stored until approved.
- The ingestion embedding is **wording-based on purpose**: four dropped words in a disclaimer must count. Search would add a meaning-based embedding.
- Role scoping is a **filter before retrieval**, shown on the store with two roles.
