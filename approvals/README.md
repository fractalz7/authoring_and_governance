# Approvals: human gates on every finding (LangGraph)

> Illustrative demo for a take-home exercise. All documents, names, figures and approvals are made up.

Picks up where [`../ingestion`](../ingestion) ends. Each finding from document 2 runs through a LangGraph workflow: AI decides only exact duplicates, every other finding pauses for a named human, a role check refuses decisions from the wrong role, and approved changes are published to Chroma as new units or new versions.

## Files

| File | What it is |
|---|---|
| `approvals_book.ipynb` | The demo notebook. Saved with outputs, so it reads without running |
| `pipeline.py` | The ingestion code as a module, generated from `../ingestion/ingestion_book.ipynb` |
| `build_approvals.py` | Regenerates `pipeline.py` and the notebook (`python3 build_approvals.py`) |
| `decisions.txt` | Timestamped decision log from the saved run: one line per decision or refused attempt, appended as it happens |

The test documents and ontology are read from `../ingestion/`.

## The graph

`route` → `auto_link` (exact duplicates, AI decides) or `human_review` (pauses; human only) → `check_role` → `apply`, or `refuse` and back to `human_review` if the wrong role decided.

| Finding | Reviewer | Approve | Reject |
|---|---|---|---|
| Exact duplicate | AI | linked automatically | — |
| Legal wording differs | Legal | new wording becomes v2 for every channel; v1 superseded | approved wording stays; document sent back |
| Contradiction | Legal | new fact becomes v2 | approved fact stands; sent back |
| Stale | Legal | confirmed stale; not published, author asked to fix | flag dismissed; published |
| Variant | Author | published as a scoped variant | sent back |
| Same meaning | Author | merged: approved unit also cites the new doc | sent back |
| New unit | Legal or author, by compliance class | published | sent back |

## What the run shows

- 2 exact duplicates linked with no human; 19 findings pause (7 for Legal, 12 for the author).
- The author tries to approve Legal's pricing-disclaimer item: **refused**, still waiting. Legal then rejects it, so the v3.2 wording stays live.
- Legal adopts the outreach wording of the recording disclosure: it is published as **v2 for every channel**, v1 kept as superseded. An inbound advocate's search now returns v2.
- The author rejects a "same meaning" merge she recognises as a real contradiction (preferred-pharmacy copays): the human catches what the offline rules missed.
- Full audit trail per decision from LangGraph's saved checkpoints.

## Run it

`pip install chromadb langgraph numpy`, then open the notebook from this folder and run all cells. In Colab, upload the notebook, `pipeline.py`, the two test docs and the ontology JSON (the first cell prompts for missing files).

Decisions are made in a cell with `decide(uid, decision, by, role)`. Each one is appended to `decisions.txt` (ISO timestamp, unit, finding, reviewer, event, who, approval ID, effect, note); each run adds a header line, so earlier runs stay in the file. In Colab the notebook also downloads it. Graph state itself is in memory and resets on restart; in production the checkpoints and decision log would go to a database.
