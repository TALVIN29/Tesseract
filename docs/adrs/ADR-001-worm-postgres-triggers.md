# ADR-001: WORM Enforcement via PostgreSQL Triggers
**Status:** Accepted | **Date:** 2026-06-08 | **Sprint:** 0

## Context
The Cube's Audit Ledger must be immutable. Application-layer immutability (e.g., simply not calling UPDATE/DELETE in code) is insufficient because it can be bypassed by future code changes, direct DB admin access, or misconfiguration.

## Decision
Enforce WORM at the PostgreSQL database layer via `BEFORE UPDATE` and `BEFORE DELETE` triggers on the `audit_ledger` table. These triggers unconditionally `RAISE EXCEPTION` regardless of the caller's identity or role. Additionally, the `cube_api` role is granted only `INSERT` and `SELECT` permissions — no `UPDATE` or `DELETE` grants exist.

This creates two independent enforcement layers:
1. Missing grants prevent the `cube_api` role from issuing UPDATE/DELETE commands.
2. Triggers prevent any role (including superuser via ORM bypass) from modifying rows.

## Consequences
- Positive: Immutability is enforced at the database layer, independent of application code.
- Positive: Any future developer who attempts to write UPDATE/DELETE logic will receive immediate feedback from the DB.
- Negative: The init.sql self-test deletes a test row using the superuser. This is the only permitted DELETE, at initialization time, before the triggers are technically "in production use."
- Negative: There is no UPDATE path for corrections — errors in Audit Ledger entries require a new entry with a `corrects_entry_id` field (Phase 2 enhancement).
