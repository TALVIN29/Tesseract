---
id: schema-fact-rule-loosened
type: decision
title: A [fact] must be verifiable, not necessarily cited
created: 2026-07-23
status: active
confidence: high
publish: true
tags: [tesseract, schema, ontology]
---

# A [fact] must be verifiable, not necessarily cited

The original `schema.md` §4 required every `[fact]` line to be backed by a `cites` relation or
a `sources:` entry. That rule broke on the third note ever written.

## Observations

- [result] 2 of the first 3 notes violated the rule — `lotclock-liquidity-over-price` and `right-censoring` #verified-by-grep
- [fact] The rule assumed every fact comes from an external document. Many do not: some are things I verified myself by reading my own code, data, or job output #verified
- [gotcha] Under the strict rule, the honest way to record "I checked this myself" was to downgrade it to `[claim]` — which would have made `[claim]` mean two different things: *unverified assertion* and *verified but unpublished*. That collapse would have destroyed the distinction the label exists for
- [decision] `[fact]` now requires that the claim be **verifiable** — either a citation, or a stated method of checking (`#verified`, a file path, a job id)
- [because] The point of separating `[fact]` from `[claim]` is to stop unverified assertions hardening into facts. That purpose is served by recording *how* you know, not by requiring the knowledge to live in an external file
- [because] A rule that the author breaks two times in three would be routinely ignored, and an ignored rule is worse than no rule — it makes the schema look enforced when it is not
- [question] Should the validator eventually check that a `#verified` tag is accompanied by *something* concrete, or is that unenforceable in practice?

## What this is evidence of

This is Phase 0 working as designed. The plan's stated purpose for hand-writing twenty notes
before any code was to find exactly this — a schema that fights the author — while changing it
is still free. It surfaced at note 3, not note 300.

## Relations

- part_of [[Tesseract]]
- supersedes [[Schema v0 Fact Rule]]
- relates_to [[Ontology Design]]
