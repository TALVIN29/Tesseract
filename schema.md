# schema.md — the ontology

This file is the contract. It is handed to the language model on every call, and it is what the
validator checks against. **A note that violates this file is rejected, not silently fixed.**

If you find yourself fighting the schema, change *this file* — deliberately, in a commit of its
own — rather than writing notes that break it.

---

## 1. Every note is one markdown file

```
---
<frontmatter>
---

# <title>

## Observations
- [label] a fact #tag

## Relations
- relation_type [[Target Note]]
```

The `## Observations` and `## Relations` headings are load-bearing — the parser looks for them
by name. Free prose may go anywhere; it is preserved but not parsed.

---

## 2. Frontmatter

| Field | Required | Allowed values | Notes |
|---|---|---|---|
| `id` | yes | kebab-case, unique, stable | The primary key. **Never reuse or recycle an id.** |
| `type` | yes | `source` `concept` `project` `decision` `experiment` | See §3 |
| `title` | yes | free text | Human-readable. What `[[links]]` point at |
| `created` | yes | `YYYY-MM-DD` | Never changes |
| `updated` | no | `YYYY-MM-DD` | Set on every edit |
| `status` | yes | `active` `superseded` `draft` | See §6 |
| `confidence` | yes | `high` `medium` `low` | How sure you are. See §7 |
| `publish` | yes | `true` `false` | **Defaults to `false`.** The entire private/public boundary |
| `sources` | no | list of paths under `raw/` | What this note was derived from |
| `tags` | no | list of kebab-case strings | Free-form grouping |

```yaml
---
id: purityloop-small-object-blindness
type: experiment
title: Small objects are the real bottleneck
created: 2026-07-19
updated: 2026-07-20
status: active
confidence: high
publish: false
sources: [raw/sources/jobs-4242-4247-recall-by-area.md]
tags: [capstone, yolo, segmentation]
---
```

---

## 3. Node types — exactly five

| Type | What it is | Folder | Test for "is this the right type?" |
|---|---|---|---|
| `source` | Something **someone else** made — paper, article, transcript, reply, dataset card | `raw/sources/` | Did I write it? If no → `source` |
| `concept` | An idea that exists independent of me | `wiki/concepts/` | Would this still be true if I'd never worked on it? |
| `project` | A thing I am building | `wiki/projects/` | Does it have a repo, a deadline, or a deliverable? |
| `decision` | A choice I made **and the reason** | `wiki/decisions/` | Could I have chosen otherwise? |
| `experiment` | A thing I ran **and what came out** | `wiki/experiments/` | Is there a number? |

**Do not invent a sixth type.** If something doesn't fit, it is almost always a `concept` with
the wrong title, or a `decision` you haven't admitted was a decision. If you genuinely need a
sixth after twenty real notes, edit this file first.

The daily journal (`log/YYYY-MM-DD.md`) is **not a type**. It is a dated stream, not a thing
with an identity, and it is not parsed for observations or relations.

---

## 4. Observation labels — exactly seven

Format: `- [label] the fact #optional-tag`

| Label | Means | Rule |
|---|---|---|
| `[fact]` | Verified. I checked it | **Must be supported by a `cites` relation or a `sources` entry** |
| `[claim]` | Someone asserts it; I have not checked | Name who, if known. Promote to `[fact]` only after verifying |
| `[decision]` | I chose X | Only in `type: decision` notes |
| `[because]` | The reason for the decision above | **Every `[decision]` must be followed by at least one `[because]`.** This is the rule the whole system exists to enforce |
| `[result]` | A measured outcome | **Must contain a number.** No number → it's a `[claim]` |
| `[question]` | Open, unresolved | Resolve it by adding a `[fact]` and deleting the question |
| `[gotcha]` | The thing that bit me | The most valuable line you will ever write. Be specific about the trap |

**One fact per line.** If a line contains "and", consider splitting it.

### Why `[claim]` and `[fact]` are different

The most common way a research record rots is a claim hardening into a fact without anyone
verifying it. Keeping them apart makes the promotion an explicit act. A `[claim]` that has sat
unverified for months is itself a finding.

---

## 5. Relation types — exactly seven

Format: `- relation_type [[Target Note Title]]`

| Relation | Direction | Means |
|---|---|---|
| `cites` | this → source | This note draws on that source |
| `part_of` | this → project | This belongs to that project |
| `supersedes` | new → old | This replaces that. **Set the old note's `status: superseded`** |
| `contradicts` | this ↔ other | These two disagree and it is not yet resolved |
| `tests` | experiment → concept | This experiment tests that idea |
| `led_to` | decision → consequence | That happened because of this |
| `relates_to` | either | Escape hatch. Use when nothing else fits, not when you're being lazy |

`supersedes` and `contradicts` are the two that make the audit real. Everything else is
navigation; these two are truth maintenance.

### Handling a retraction

Do **not** delete or edit the wrong note. Instead:

1. Write a new note explaining what is actually true.
2. Add `- supersedes [[The Old Note]]` to the new one.
3. Set the old note's `status: superseded`.

The wrong answer stays readable, with a pointer to the right one. That is how you keep the
record of *having been wrong*, which is usually more instructive than the correction.

---

## 6. `status`

| Value | Means |
|---|---|
| `active` | Current. Trust it |
| `superseded` | Replaced. Something else `supersedes` it. **Kept, never deleted** |
| `draft` | Captured but not yet reviewed by a human |

Notes with `status: superseded` are excluded from search results by default and from the public
site always.

---

## 7. `confidence`

| Value | Means |
|---|---|
| `high` | Verified, or I ran it myself |
| `medium` | Reasoned but unconfirmed |
| `low` | A hunch. Written down so I don't lose it, not because I trust it |

This field is the honesty machine. Without it, an AI-maintained wiki drifts into confident
nonsense, because nothing records that you weren't sure. A `low` note that has never been
revisited is a finding the weekly review reports.

---

## 8. Rules for automated processing

These bind the pipeline, not you.

1. **`raw/` is frozen.** Automation may create files in `raw/`. It may **never** edit or delete
   one. Everything else in the repository can be rebuilt from `raw/`; this rule is what makes
   that true, and therefore what makes AI-proposed edits safe to accept.
2. **Propose, never apply.** All automated changes to `wiki/` arrive as a pull request. Nothing
   merges without a human.
3. **Validate before writing.** Any model output that violates this schema is retried up to
   three times with the error fed back. On the third failure, write the item to
   `raw/inbox/` with `status: draft` and a note explaining the failure. **A note that says
   "I could not parse this" is acceptable. A silently malformed note is not.**
4. **Never invent a `[because]`.** If the reason for a decision is not present in the source
   material, emit `- [question] why was this chosen?` instead. A fabricated rationale is worse
   than a missing one, because it is indistinguishable from a real one later.
5. **Never promote `[claim]` to `[fact]`.** Only a human does that.
6. **`publish` defaults to `false`** and is never set to `true` by automation.
7. **If an index and a note disagree, the note wins.** Indexes in `index/` are derived and
   disposable.

---

## 9. Worked example

```markdown
---
id: fl-gamma-arm-invalid
type: experiment
title: focal_gamma_15 was never a real experiment
created: 2026-07-19
status: active
confidence: high
publish: false
sources: [raw/sources/fathey-reply-2026-07-19.md]
tags: [capstone, purityloop, retraction]
---

# focal_gamma_15 was never a real experiment

## Observations
- [claim] Dr Fathey: YOLOv8 no longer supports focal loss / fl_gamma
- [fact] Confirmed — fl_gamma absent from final_integration.zip args.yaml #verified
- [result] focal_gamma_15 is configuration-identical to ctrl_baseline — 0 distinct arms
- [gotcha] The dead knob is still referenced in train_chris.py, compare_results.py,
  PURITYLOOP_PLAYBOOK.md and team_next_steps_post_baseline.md
- [question] Redo class imbalance via cls weight, sampling, or class_weights.csv?

## Relations
- part_of [[PurityLoop]]
- contradicts [[Focal Loss Experiment Plan]]
- tests [[Class Imbalance]]
- cites [[raw/sources/fathey-reply-2026-07-19.md]]
```

Note the shape: a `[claim]` from a person, promoted to `[fact]` only after being checked
against a file, with the resulting invalidation recorded as `contradicts` rather than by
deleting the old plan.
