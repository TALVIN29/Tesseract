# purpose.md — what this hub is for

Handed to the language model alongside `schema.md`. `schema.md` says what a valid note looks
like; this file says what a *good* one looks like, and what the hub is trying to prevent.

---

## The problem this exists to solve

> A solo researcher's reasoning is destroyed by time. What was measured survives in files; why
> it was chosen, what was already ruled out, and which results were later invalidated exist only
> in memory — and memory fails inside a single project's lifetime.

In a 2016 Nature survey of 1,576 researchers, more than 70% had failed to reproduce another
scientist's experiment, and **over half had failed to reproduce their own**. Thoughtworks
describes the same failure in software: teams asking why a technology was chosen and getting
back *"I think latency was the issue… someone on the old team preferred it…"* — their phrase is
that architecture **drifts into folklore**.

This hub exists to stop that happening to one person's work.

---

## The eight questions it must be able to answer

Every design choice is judged against these. If a feature serves none of them, it is decoration.

| # | Question |
|---|---|
| Q1 | Why did I choose X over Y, and what did I know at the time? |
| Q2 | What did experiment E actually measure, and is that number still valid? |
| Q3 | Which of my conclusions have since been retracted or superseded? |
| Q4 | What have I already ruled out, so I don't retry it? |
| Q5 | What does source S claim, and which of my notes depend on it? |
| Q6 | What do I believe with low confidence that I never went back and confirmed? |
| Q7 | Which two notes contradict each other? |
| Q8 | What did I work on in month M? |

**Q1–Q4 are the product.** Q5–Q8 are hygiene.

---

## What a good note looks like

- **A decision note without a `[because]` has failed.** It records the outcome and loses the
  reasoning, which is the exact failure this hub exists to prevent.
- **An experiment note without a number has failed.** "It worked better" is not a result.
- **A `[gotcha]` is worth more than three `[fact]`s.** The trap that cost you a day is the
  thing you will re-read.
- **Being wrong, recorded, is more valuable than being vaguely right.** Retractions stay. See
  `schema.md` §5.
- **Short and specific beats long and hedged.** One line per fact.

## What a bad note looks like

- A summary with no source.
- A fabricated `[because]` — inferred rather than recorded. If the reason isn't in the material,
  write `- [question] why was this chosen?` instead. A plausible invented rationale is worse
  than an admitted gap, because later you cannot tell them apart.
- A `[claim]` written as a `[fact]`.
- A wall of prose with no observations, which the graph and the audit cannot see.
- A note that restates what a linked note already says instead of linking to it.

---

## Who this is for

**Primary user: one person.** A tool for this problem whose author doesn't use it daily is
worthless.

**Plausible wider audience: applied-ML postgraduates and early-career researchers.** They fall
through a real gap:

- MLflow and Weights & Biases assume a tracking server, a team, and MLOps setup. This audience
  has a shared university HPC and no permission to install infrastructure.
- Architecture Decision Records assume decisions happen in pull request reviews. Here they
  happen in supervisor meetings — spoken, and never written down.
- Both assume a team that inherits the work. Here the audience is one supervisor and,
  eventually, an examiner.

They also have a forcing function most tool audiences lack: a thesis defence, where *"why did
you choose this?"* is asked out loud about a decision made eleven months earlier, by someone
qualified to notice a reconstructed answer.

**Unproven, and treated as a hypothesis rather than a fact:** that this audience would adopt
someone else's tool. Researchers tend to prefer their own hacks. The cheap test is to show two
lab-mates and see whether they ask for it.

**Not claimed:** a market, a business, or revenue.

---

## The three layers

| Layer | Directory | Rule |
|---|---|---|
| **Cube** — solid | `raw/` | Never edited, never deleted by automation. Everything else rebuilds from here |
| **Planes** — transitional | `pipeline/` | Turns messy input into structured notes. **Proposes only** |
| **Sphere** — liquid | `wiki/` | The AI may rewrite freely — *because* the Cube can regenerate it |

That last clause is the whole safety argument. The worst outcome of a bad automated edit is
"regenerate the wiki", never "lose the source". This is why AI-proposed changes are acceptable
at all, and why rule 1 in `schema.md` §8 is non-negotiable.

---

## What this hub is not

- **Not a general note-taking app.** Obsidian is better at that, and should be used as the
  editor over this same folder.
- **Not a task manager.** No todos, no due dates, no kanban.
- **Not a journal.** `log/` exists, but it is a dated stream, not the point.
- **Not a chatbot.** The model's job is to structure and maintain, not to converse.
