# Archive — what this was, and why it isn't that any more

Everything in this folder is the **original Project Tesseract** (June 2026): an elaborate
specification for an AI-augmented compliance platform called the *Fractal-State Engine*.

It described a "Dual-Core Damping" topology — an Outer Sphere (liquid, AI/UI), 2D Damping
Planes (n8n workflow mesh), and an Inner Cube (solid, immutable compliance core with twelve
protocol "edges"). It specified risk verdicts (`WATCHLIST` / `SUSPEND` / `NEAR_MISS`), a WORM
Postgres audit ledger, a Redis shock-absorption queue, Prometheus and Grafana monitoring, and
a twelve-week six-sprint delivery plan.

## Why it was archived

**No Python file in this repository ever imported any of it.** The `docker-compose.yml`, the
four JSON schemas, the three ADRs, and 80 KB of PRD described a system that was never built —
while the code that *was* built (`main.py`, `store.py`, `ai.py`) was a knowledge hub with no
relationship to compliance at all.

The repository was two projects wearing one name.

## What survived

The three-layer idea was the good part. It was simply pointed at the wrong subject.

Re-aimed at **knowledge** rather than compliance, the layers become accurate:

| Layer | Original meaning | What it means now |
|---|---|---|
| **Cube** (solid) | Immutable compliance rules | `raw/` — captured sources, never edited, never deleted by automation |
| **Planes** (phase transition) | n8n workflow mesh | `pipeline/` — turns messy input into structured notes, proposes only |
| **Sphere** (liquid) | AI-driven UI | `wiki/` — notes the AI may freely rewrite, *because* the Cube can regenerate them |

The PRD's own claim — *"external chaos is absorbed, filtered, and neutralized before it ever
reaches the immutable core"* — is now literally true of the system, which it never was of the
one described here.

The twelve Edges became the ontology: five node types, seven observation labels, seven relation
types. See `../../schema.md`.

## Why keep it instead of deleting it

Deleting it would hide the most useful thing in the repository's history: the evidence that an
80 KB specification with docker-compose files and sequence diagrams can describe a system that
does not exist, and that noticing this is worth more than defending it.

Also archived here:

- `sample-knowledge/`, `sample-meetings/` — placeholder engineering/HR content from the
  original prototype, kept only as examples of the old `dept`-based folder layout.
- `app.py` was **deleted**, not archived — it was a dead Gradio interface importing four
  functions (`generate`, `search_github_sops`, `fetch_github_content`, `adapt_sop`) that no
  longer existed in `ai.py`, so it could not be imported at all. Recoverable from git history.
