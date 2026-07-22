# CHECKPOINT — 2026-07-23

**Read this first when resuming.** Current state, what's next, and the decisions already made
so they don't get re-litigated.

Plan lives at `C:\Users\Talvin\.claude\plans\i-want-to-build-dynamic-creek.md`.

---

## Where we are

**Phase 0, day 2 of 5.** Ontology written, 4 of 20 notes done.

| Phase | State |
|---|---|
| 0 — ontology + 20 hand-written notes | **in progress — 4/20** |
| 1 — capture (issue → file in repo) | not started |
| 2 — pipeline + PR output | not started |
| 3 — embeddings, audit, Quartz, deploy | not started |
| 4 — weekly review rewrite | not started |
| 5–7 — news, broadcast, classifier | optional, deferred |

Commits: `a5cf074` (restructure), `e6fd8be` (first notes). Pushed to `origin/master`.

---

## What this project is

A knowledge hub that records **why you chose** and **what you measured**, and keeps it
retrievable months later.

The validated problem, not an invented one: a 2016 Nature survey of 1,576 researchers found
>70% had failed to reproduce another scientist's experiment, and **over half had failed to
reproduce their own**. Thoughtworks calls the software version of this "architecture drifting
into folklore". ADRs solve the *why* half for teams; MLflow/W&B solve the *what* half for teams
with infrastructure. Nobody serves the solo researcher who has a shared HPC, a supervisor, and
a defence at the end.

Full reasoning: `purpose.md`. Evidence and audience: plan §1.

---

## Decisions already made — do not reopen

| Decision | Why |
|---|---|
| **Serverless. No FastAPI, no localhost** | Workload is events + a clock, not requests. A permanent server idles 23h55m/day |
| **Markdown in git is the database** | Git gives history, transactions, rollback, backup, audit log. Indexes are derived and disposable |
| **Capture = GitHub Issues from the phone** | Zero infrastructure. Capture must never require a decision |
| **AI proposes via Pull Request, never writes directly** | Durable, diffable, reviewable from bed. Replaces the old in-memory `pending` queue |
| **`raw/` is frozen** | The whole safety argument. Worst case is "rebuild the wiki", never "lose the source" |
| **Ollama for private notes, Gemini for public news** | Gemini's free tier may train on prompts — private notes must never go there |
| **Quartz 5 → Cloudflare Pages** | Free. Client-side search + graph, no backend |
| **Bluesky + Telegram, not X** | X went pay-per-use Feb 2026 (~$0.015/post) |
| **Keep the Sphere/Planes/Cube metaphor, re-aimed** | The three-state idea was right, just pointed at compliance instead of knowledge |
| **Archive the fictional PRD, don't delete it** | The visible pivot is a better story than pretending it was always right |
| **`[fact]` = verifiable, not necessarily cited** | Broke at note 3. See `wiki/decisions/schema-fact-rule-loosened.md` |

**Total running cost: $0/month.** Every component is open source or a permanent free tier.

---

## Layout

```
schema.md      the contract — 5 types, 7 fact labels, 7 relations, 7 automation rules
purpose.md     the 8 questions the hub must answer
raw/           THE CUBE — frozen. inbox/ sources/ news/ log.md
wiki/          THE SPHERE — concepts/ projects/ decisions/ experiments/
log/           daily journal + log/reviews/
pipeline/      THE PLANES — empty until Phase 2
site/          Quartz config — empty until Phase 3
index/         derived, gitignored
docs/archive/  the original PRD, infra, schemas, ADRs, sample data
main.py store.py ai.py static/ tests/   <- legacy, ported in Phase 2, then deleted
```

---

## Notes written so far (4/20)

| File | Type | Why this one |
|---|---|---|
| `wiki/experiments/purityloop-small-object-blindness.md` | experiment | Real recall-by-area numbers. The root-cause finding |
| `wiki/decisions/lotclock-liquidity-over-price.md` | decision | The pivot reasoning, with 4 `[because]` lines |
| `wiki/concepts/right-censoring.md` | concept | The stats idea LotClock depends on |
| `wiki/decisions/schema-fact-rule-loosened.md` | decision | The schema breaking, recorded by the system itself |

---

## Open gaps — known, not hidden

1. **Dangling source.** `purityloop-small-object-blindness.md` cites
   `raw/sources/jobs-4242-4247-recall-by-area.md`, which does not exist. That data is job
   output on the HPC. Capture it.
2. **Unsourced claims.** `right-censoring.md` has four `[claim]` lines that are textbook
   material. Capture a survival-analysis reference into `raw/sources/` and promote them.
3. **Dangling links.** `[[PurityLoop]]`, `[[LotClock]]`, `[[Tesseract]]`, `[[Class Imbalance]]`,
   `[[Small Object Detection]]` and others point at notes not yet written. Intended — a dangling
   link marks something worth writing.
4. **Legacy code still at repo root.** `main.py`, `store.py`, `ai.py`, `static/`, `tests/`
   remain until Phase 2 ports the useful parts into `pipeline/`. `requirements.txt` is still
   wrong (missing fastapi, uvicorn, chromadb, pdfplumber, pydantic) — it gets replaced
   wholesale in Phase 2, so it is deliberately not being patched now.

---

## Next actions, in order

### Finish Phase 0 — 16 more notes (~4 hours)

Write them **by hand**. The point is to feel the friction while the schema is still free to
change. Suggested sources, all real material that already exists:

- **Capstone / PurityLoop** — the fl_gamma retraction (`schema.md` §9 has it written already,
  lift it); the stale-dataset gotcha (local copy gives wrong answers, use the HPC copy); the run
  history table (v3_ffremask_9cls 0.585 is still the best); the `results.csv` time-column reset
  gotcha; the HPC/Slurm setup as a `project` note; the supervisor reporting chain as a
  `decision`.
- **LotClock** — the scraping ethics stance (three sites excluded on principle); the daily
  scraper architecture; the Porter analysis conclusion; day-0 collection date.
- **CareerOS** — the `calculatePostingIntegrity` rules-engine design; why a transparent rules
  engine rather than an LLM.
- **Tesseract itself** — a `project` note; the serverless decision; the git-as-database
  decision.

**Gate to pass:** 20 notes written and you did not need a sixth node type. If you find yourself
wanting one, edit `schema.md` deliberately in its own commit and record the reason as a
`decision` note — same as `schema-fact-rule-loosened.md`.

### Then Phase 1 — capture (~3–4 hours)

`.github/workflows/capture.yml` — on issue opened, write the body to `raw/inbox/`, comment with
a link, close the issue. Watch for: the workflow needs `contents: write` permission to commit to
its own repo, and the error when it lacks it is unhelpful.

**Gate:** open an issue from the phone app, away from your desk. File appears in the repo in
under 60 seconds, and capture took under 30 seconds of your attention.

---

## Checks that should keep passing

Every `[fact]` line must be verifiable — cited, or carrying a stated method of checking:

```bash
cd /e/Portfolio/Tesseract
for f in wiki/*/*.md; do
  hs=$( (grep -q '^sources:' "$f" || grep -q 'cites \[\[' "$f") && echo 1 || echo 0)
  grep '^- \[fact\]' "$f" | while IFS= read -r line; do
    [ "$hs" = "0" ] && ! echo "$line" | grep -qE '#[a-z-]*verified|\.md|\.py|job [0-9]' \
      && echo "UNVERIFIED  $f: $line"
  done
done
```

Every `[decision]` must be followed by at least one `[because]`:

```bash
cd /e/Portfolio/Tesseract
for f in wiki/decisions/*.md; do
  d=$(grep -c '^- \[decision\]' "$f"); b=$(grep -c '^- \[because\]' "$f")
  [ "$d" -gt 0 ] && [ "$b" -eq 0 ] && echo "NO REASON  $f"
done
```

Both become real code in Phase 3 (`pipeline/audit.py`). Until then, run them by hand.

---

## Kill criteria — decided in advance, on purpose

At 12 weeks: if captures are under 5/week **and** the inbox has never cleared **and** you cannot
name one specific time this saved you work — **stop**. Keep the markdown folder, delete the
automation. The folder alone was already most of the value.

Deciding this now is cheaper than deciding it while attached.
