# Where an LLM is used in the ingestion flow

> Illustrative demo for a take-home exercise. Made-up data only.

The notebook (`ingestion_book.ipynb`) runs fully offline. Claude is optional in three places, each with a rule-based fallback. Everything else is rules: some of it because the test docs are clean, some of it on purpose.

## Where Claude is used today (optional)

| Step | What Claude does | Offline fallback |
|---|---|---|
| Tagging | Picks the unit type and topic for each unit | Keyword counts against the ontology |
| Summary | Writes the two-sentence document summary | Template built from document details and tags |
| Judging a matched pair | Decides whether two guidance units are same meaning, variant, contradiction or stale | Compares figures, checks for retired terms, checks channel |

Set `ANTHROPIC_API_KEY` (or, in Colab, add it under Secrets) to turn it on.

## What is rules, and why

- **Splitting documents into units and reading document details:** rules. This works only because the test scripts are clean markdown with a header table and `[VERBATIM – LEGAL]` markers.
- **Embeddings, exact duplicates, routing:** rules, because they are mechanical.
- **Sending legal verbatim to Legal:** rules, **on purpose**. Any change to legal wording goes to a human, whatever a model thinks. This is a design choice, not a gap.

## Where a real deployment would need Claude (not in the demo)

1. **Splitting messy documents.** Real Word files and PDFs have no markers. Finding unit boundaries, and spotting legal verbatim nobody marked, is the hardest and most valuable AI work in the flow.
2. **Pulling document details** when there is no clean header (author, effective date, plan year from a footer or cover page).
3. **Contradictions in claims, not just numbers.** Example: "preferred copays apply at all network pharmacies." The offline rules miss this one.
4. **Proposing a fix:** a merged wording, or an update for a stale unit, for the author to edit.
5. **Gap questions:** turning an unanswered question into a proposed new unit.
6. **Readable preview lines** for the units table.

## Where Claude should never be used

Approving content, resolving legal conflicts, granting a role access to a knowledge base. These match the "human only" column of the brief.

## Known risk for the demo

The rubric scores "AI that does real work." With clean test docs, the offline rules can look like they are doing that work. To make it stronger: run with Claude on, and add a third, unmarked test document (for example a plain-prose benefit memo) where Claude must find the units and the verbatim itself.
