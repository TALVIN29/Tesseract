# ADR-003: The Inner Cube Has No Outbound Network Routes
**Status:** Accepted | **Date:** 2026-06-08 | **Sprint:** 0

## Context
The Fractal-State Engine requires absolute architectural separation between the Outer Sphere, 2D Planes, and Inner Cube. The Cube is the immutable compliance core — it must not be reachable from the Sphere directly, and it must not initiate any outbound communication.

## Decision
The Inner Cube Fastify API:
1. Exposes exactly one inbound endpoint: `POST /api/v1/cube/evaluate`
2. Has zero outbound HTTP or network calls
3. Is not accessible from the Sphere API gateway (blocked at Next.js middleware layer)
4. Only accepts connections from the Plane network via mTLS + service account JWT

Any request that arrives at the Cube without a valid Plane mTLS client certificate triggers the Cube Lockdown Protocol (TESS-033/034).

## Consequences
- Positive: The Cube cannot be used as a vector for data exfiltration or lateral movement.
- Positive: All compliance decisions are synchronous (request/response) — no async side effects originating from the Cube.
- Negative: The Cube cannot proactively push verdicts. All verdict delivery relies on the Plane calling `POST /api/sphere/notify` after receiving the Cube's synchronous response. This creates the orphaned `job_id` race condition (Audit Finding 1) which is mitigated by Patches 1A/B/C.
- Negative: The Cube cannot self-update its rule set. Rule changes require a restart to reload YAML from `CUBE_RULES_PATH`. Hot reload is explicitly deferred to Phase 2.
