# PROJECT TESSERACT â€” ARCHITECTURAL AUDIT & EXECUTION PLAN
### Red Team Review + Ticket-Level Progress Plan
**Status:** Sprint 0 Complete — Sprint 1 Ready | **Date:** 2026-06-08

---

# PART 1: ARCHITECTURAL AUDIT & PRD REFINEMENTS

> Red Team scope: race conditions, state management under failure, and API contract gaps. Three critical findings, each with a required patch.

---

## FINDING 1 â€” RACE CONDITION: Orphaned `job_id` on WebSocket Notify Failure

**Severity:** Critical  
**Location:** Deliverable 3 â†’ Chemical Reaction Interface sequence

### The Problem

The current async chain is:

```
Plane â†’ POST /cube/evaluate â†’ Cube responds â†’ Plane calls POST /sphere/notify â†’ WebSocket push
```

The `POST /sphere/notify` call from the Plane to the Sphere is **not covered by the exponential backoff contract**. Only the Plane-to-Cube call (`NearMissPacket` emission) has a defined retry policy. If the WebSocket connection drops, or if the Sphere's notify endpoint is temporarily unreachable between the Cube writing the Audit Ledger entry and the Plane dispatching the notify, the following state is produced:

- Cube: verdict written, `audit_ledger_entry_id` exists. âœ“
- Plane: verdict received, notify call failed silently. âœ—
- Sphere: holds a `job_id` with no corresponding verdict. UI is permanently stuck in a `PENDING` state with no timeout handler defined.

The Sphere UI has no mechanism to escape this state. There is no polling fallback, no `job_id` TTL, and no reconnection reconciliation defined anywhere in the current PRD.

### Required Patches

**Patch 1A â€” Add `GET /api/sphere/verdict/{job_id}` reconciliation endpoint.**  
The Sphere must be able to poll for a verdict by `job_id` on WebSocket reconnect or after a configurable client-side timeout. This endpoint reads from the Audit Ledger (read-only path â€” does not touch the Cube directly).

**Patch 1B â€” Add `PROCESSING_TIMEOUT` UI pseudo-state.**  
The Sphere must implement a `job_id` registry in local state (e.g., React context or Zustand store). Any `job_id` that has not received a WebSocket verdict push within **30 seconds** transitions to `PROCESSING_TIMEOUT` state, surfacing a recoverable error component in the Antigravity grid. On WebSocket reconnect, the Sphere iterates all outstanding `job_id`s and calls the reconciliation endpoint.

**Patch 1C â€” Add exponential backoff to `POST /api/sphere/notify`.**  
The Plane's notify call to the Sphere must use the same retry policy as the Cube call (100ms, 200ms, 400ms, 800ms, cap 5s). This is a one-line config change in the Near Miss Event Emitter n8n workflow but must be explicitly specified in the PRD to prevent it being omitted in implementation.

---

## FINDING 2 â€” STATE MANAGEMENT: Redis Drop Leaves Sphere in Unrecoverable Limbo

**Severity:** High  
**Location:** Deliverable 1 â†’ PLN-005 (Shock Absorption Queue) + Deliverable 3 â†’ Stack

### The Problem

The Sphere submits an event and immediately receives `202 Accepted` + `job_id`. The message is written to a Redis Stream. The current PRD defines no:

- **Message TTL** â€” a message can sit in the stream indefinitely if all Plane consumers are offline.
- **Dead Letter Queue (DLQ)** â€” if a consumer group acknowledges receipt but processing fails (e.g., n8n workflow crash mid-execution), the message is lost with no recovery path.
- **Poison message handling** â€” a malformed SegmentationPayload that passes the API gateway but fails Plane-side schema validation will be retried indefinitely by the consumer group, blocking the stream partition.

The consequence: the Sphere UI holds a `job_id` that maps to a message that is either stuck, lost, or poison. From the user's perspective, their action disappeared.

### Required Patches

**Patch 2A â€” Add Redis Stream DLQ.**  
Messages that fail Plane-side processing after 3 attempts must be moved to a dedicated `tesseract:dlq` stream. The DLQ is monitored by the Plane Self-Diagnostics workflow (`PLN-006`), which emits a `RULE_GAP_EXPOSURE` signal to the Cube for any DLQ entry (since an unprocessable message is a gap in the system's defensive coverage).

**Patch 2B â€” Define message TTL.**  
All Redis Stream messages must have a TTL of **120 seconds**. On TTL expiry without consumer acknowledgment, the message is moved to the DLQ (not silently dropped). This requires Redis Stream MAXLEN or a TTL management workflow in n8n.

**Patch 2C â€” Add `job_id` status field to Sphere API response contract.**  
The `202 Accepted` response must be extended:

```yaml
# CURRENT (insufficient)
{ "job_id": "abc123" }

# PATCHED
{
  "job_id": "abc123",
  "status": "QUEUED",           # QUEUED | PROCESSING | VERDICT_RECEIVED | TIMEOUT | DLQ
  "ttl_seconds": 120,
  "poll_endpoint": "/api/sphere/verdict/abc123"
}
```

---

## FINDING 3 â€” API CONTRACT GAPS: Three Missing Definitions Break Layer Decoupling

**Severity:** Critical  
**Location:** Deliverable 3 â†’ NearMissPacket Schema + CubeVerdictResponse Schema

### Gap 3A â€” `SegmentationPayload` is `$ref`'d but never defined

Both `NearMissPacket` and the Sphere API contract reference `SegmentationPayload` as a `$ref` to `#/components/schemas/SegmentationPayload`. This schema is **never defined anywhere in the PRD or Tech Stack Blueprint.** Without it, the Plane-to-Cube boundary has no validation contract. The minimum required definition:

```yaml
SegmentationPayload:
  type: object
  required:
    - session_id
    - entity_id_hashed
    - user_tier
    - behavioral_cohort
    - risk_band_last_known
    - session_start_timestamp
    - geo_context
  properties:
    session_id:         { type: string, format: uuid }
    entity_id_hashed:   { type: string }          # SHA-256, never raw PII
    user_tier:          { type: string, enum: [STANDARD, ELEVATED, RESTRICTED] }
    behavioral_cohort:  { type: string }          # Cohort label from AI classifier
    risk_band_last_known:
      type: string
      enum: [CLEAN, WATCHLIST, SUSPENDED, UNKNOWN]
      description: Read-only. Reflects last Cube verdict for this entity. Never written by Sphere.
    session_start_timestamp: { type: string, format: date-time }
    geo_context:
      type: object
      properties:
        country_code:   { type: string }
        region:         { type: string }
        is_vpn:         { type: boolean }
        is_tor:         { type: boolean }
```

### Gap 3B â€” Multi-signal `NearMissPacket` has no verdict aggregation contract

A `NearMissPacket` carries an **array** of `risk_signals`. The Cube's Risk Tiering Engine must reduce this array to a single verdict. The current PRD defines no aggregation contract â€” it is undefined whether the engine uses max-severity, first-match, weighted-score, or unanimous-required logic. Without this specification, two Cube deployments (e.g., staging vs. production) running different rule YAML versions could produce different verdicts for identical packets.

**Required addition to Cube YAML rule schema:**

```yaml
# Top-level field in every rule YAML file
aggregation_strategy:
  type: string
  enum: [MAX_SEVERITY, FIRST_MATCH, WEIGHTED_SUM]
  default: MAX_SEVERITY
  description: >
    MAX_SEVERITY: the highest-severity verdict among all signals wins.
    FIRST_MATCH: signals are evaluated in array order; first match terminates.
    WEIGHTED_SUM: signals contribute weighted scores; verdict is determined by threshold bands.
```

The V1 PRD must specify `MAX_SEVERITY` as the locked default for the prototype, with a note that `WEIGHTED_SUM` is the Phase 2 production target.

### Gap 3C â€” `NearMissPacket` has no `schema_version` field

`CubeVerdictResponse` correctly records `rule_version_applied` (the Git SHA of the rules used). But `NearMissPacket` has no `schema_version` field. As the packet schema evolves across sprints (new `signal_type` enum values, new `SegmentationPayload` fields), the Cube cannot distinguish a V1 packet from a V2 packet. This breaks backward compatibility and makes the Audit Ledger entries non-interpretable after a schema migration.

**Required addition to `NearMissPacket`:**

```yaml
schema_version:
  type: string
  pattern: '^v\d+\.\d+$'
  example: "v1.0"
  description: >
    Semantic version of the NearMissPacket schema used to construct this packet.
    The Cube rejects packets with schema_version values it does not support.
```

---

### AUDIT SUMMARY TABLE

| Finding | Severity | Layer Affected | Patch Count | Sprint Impact |
|---|---|---|---|---|
| F1: Orphaned `job_id` on notify failure | Critical | Sphere + Plane | 3 patches | Adds 2 tasks to Sprint 3 & Sprint 5 |
| F2: Redis drop leaves Sphere in limbo | High | Plane (Queue) | 3 patches | Adds 3 tasks to Sprint 3 |
| F3A: `SegmentationPayload` undefined | Critical | All 3 layers | 1 schema definition | Blocks Sprint 1 sign-off |
| F3B: Multi-signal aggregation undefined | Critical | Cube | 1 YAML field | Must be ratified in Sprint 1 |
| F3C: `NearMissPacket` schema versioning | Medium | Plane + Cube | 1 field addition | Adds to Sprint 1 schema task |

**All 5 findings must be resolved before Sprint 1 implementation begins.** Findings 3A, 3B, and 3C are schema-level and can be patched in the YAML/OpenAPI files before any code is written. Findings 1 and 2 require new implementation tasks inserted into the sprint plan below.

---
---

# PART 2: EXECUTION ROADMAP â€” TICKET-LEVEL PROGRESS PLAN

> This is the source of truth for the build phase. All tasks are checkboxed. No task may be marked complete without its acceptance criteria met.

---

## SPRINT 0 â€” ENVIRONMENT SETUP & SCHEMA RATIFICATION
### Duration: Days 1â€“3 (pre-Sprint 1, not counted in 12-week clock)
### Goal: Zero code written. Infrastructure running. All schemas ratified.

---

### EPIC 0: ENVIRONMENT BOOTSTRAP

#### E0-A: Repository & Version Control

- [x] **[TESS-000]** Initialize monorepo at `e:\Tesseract` with the following top-level structure:
  ```
  /cube          â†’ Fastify API (Inner Cube)
  /planes        â†’ n8n workflow exports + Node.js webhook handlers
  /sphere        â†’ Next.js 15 frontend
  /infra         â†’ Docker Compose, K8s manifests (stub), Prometheus/Grafana config
  /rules         â†’ Cube YAML rule store (separate Git repo, dual-approval)
  /schemas       â†’ OpenAPI 3.1 specs (NearMissPacket, SegmentationPayload, CubeVerdictResponse)
  /docs          â†’ Runbooks, ADRs, audit outputs
  ```
- [x] **[TESS-001]** Initialize `/rules` as a **separate** Git repository with branch protection:
  - `rules/main` requires 2 approving reviewers
  - Signed commits enforced (`gpg` or SSH signing)
  - No direct push to `rules/main` permitted
- [x] **[TESS-002]** Create `.env.example` file at repo root documenting all required environment variables:
  ```
  # Cube
  CUBE_PORT=3100
  CUBE_DB_URL=postgresql://...
  CUBE_REDIS_URL=redis://...
  CUBE_JWT_SECRET=...
  CUBE_MTLS_CERT_PATH=...
  CUBE_MTLS_KEY_PATH=...

  # Planes
  N8N_PORT=5678
  N8N_BASIC_AUTH_USER=...
  N8N_BASIC_AUTH_PASSWORD=...
  N8N_ENCRYPTION_KEY=...
  REDIS_URL=redis://...
  GOOGLE_OAUTH_CLIENT_ID=...
  GOOGLE_OAUTH_CLIENT_SECRET=...
  PLANE_TO_CUBE_JWT_SECRET=...

  # Sphere
  NEXT_PUBLIC_WS_URL=ws://...
  NEXT_PUBLIC_API_GATEWAY_URL=https://...
  SPHERE_BEARER_TOKEN_SECRET=...

  # Monitoring
  GRAFANA_ADMIN_PASSWORD=...
  ```
- [x] **[TESS-003]** Add `.gitignore` entries: `.env`, `*.pem`, `*.key`, `node_modules/`, `.next/`, `n8n-data/`

---

#### E0-B: Docker Compose â€” Full Stack Local Environment

- [x] **[TESS-004]** Create `infra/docker-compose.yml` with the following services:

  | Service | Image | Port | Notes |
  |---|---|---|---|
  | `postgres-cube` | `postgres:16-alpine` | 5433 | Cube Audit Ledger DB |
  | `postgres-planes` | `postgres:16-alpine` | 5434 | Plane state store DB |
  | `redis` | `redis:7-alpine` | 6379 | Streams + Pub/Sub + DLQ |
  | `n8n` | `n8nio/n8n:latest` | 5678 | Planes automation engine |
  | `cube-api` | `(local build)` | 3100 | Inner Cube Fastify API |
  | `prometheus` | `prom/prometheus:latest` | 9090 | Metrics scrape |
  | `grafana` | `grafana/grafana:latest` | 3001 | Dashboards |

- [x] **[TESS-005]** Configure `postgres-cube` with a startup SQL script that:
  - Creates `audit_ledger` table (schema defined in `[TESS-012]`)
  - Installs `BEFORE UPDATE` and `BEFORE DELETE` triggers that `RAISE EXCEPTION` unconditionally
  - Grants only `INSERT` and `SELECT` to the `cube_api` role (no `UPDATE`/`DELETE` grants)
- [x] **[TESS-006]** Configure Redis with `appendonly yes` and `maxmemory-policy noeviction` to prevent silent message loss under memory pressure
- [x] **[TESS-007]** Configure n8n environment variables in Docker Compose:
  - `N8N_ENCRYPTION_KEY` â€” required for credential storage
  - `N8N_BASIC_AUTH_ACTIVE=true`
  - `WEBHOOK_URL=http://n8n:5678/` â€” internal Docker network URL
- [x] **[TESS-008]** Verify full stack starts cleanly: `docker compose up -d` â†’ all 7 services `healthy`
- [x] **[TESS-009]** Verify WORM policy: attempt a SQL `UPDATE` on `audit_ledger` â†’ confirm `EXCEPTION` is raised

---

#### E0-C: Schema Ratification (Audit Patches Applied)

- [x] **[TESS-010]** Define `SegmentationPayload` schema in `/schemas/segmentation-payload.yaml` per Audit Finding 3A. Must include all 7 required fields. Reviewed and merged to `main`.
- [x] **[TESS-011]** Update `NearMissPacket` schema in `/schemas/near-miss-packet.yaml`:
  - Add `schema_version` field (Audit Finding 3C)
  - Add `signal_aggregation_hint` field (Audit Finding 3B) â€” `enum: [MAX_SEVERITY, FIRST_MATCH]`, default `MAX_SEVERITY`
  - Bump schema to `v1.0`
- [x] **[TESS-012]** Update `CubeVerdictResponse` schema in `/schemas/cube-verdict-response.yaml`:
  - Confirm `already_processed: boolean` field exists for idempotency deduplication response
  - If Cube has already processed a `packet_id`, return `already_processed: true` + original verdict (not 409)
- [x] **[TESS-013]** Update Sphere API `202 Accepted` response schema per Audit Finding 2C:
  - Add `status`, `ttl_seconds`, `poll_endpoint` fields
  - Document in `/schemas/sphere-enqueue-response.yaml`
- [x] **[TESS-014]** Peer review all 4 schema files. Sign off from Architect + Compliance Lead. Merge to `main`.

**Sprint 0 exit gate:** Docker stack healthy. All 4 schemas ratified and merged. `.env.example` complete. No code written beyond infrastructure config.

---

## EPIC 1: THE INNER CUBE
### Sprints 1â€“2 | Weeks 1â€“4

---

### SPRINT 1 â€” Cube Foundation
**Duration:** Weeks 1â€“2

#### E1-A: Fastify Application Scaffold

- [ ] **[TESS-015]** Scaffold Fastify application in `/cube`:
  ```
  /cube
    /src
      /routes       â†’ route definitions
      /plugins      â†’ auth, schema-validation, metrics
      /services     â†’ risk-engine, audit-ledger, lockdown
      /schemas      â†’ compiled JSON schemas from /schemas/*.yaml
    server.ts
    Dockerfile
  ```
- [ ] **[TESS-016]** Install dependencies: `fastify`, `@fastify/jwt`, `@fastify/postgres`, `fastify-plugin`, `zod`, `pino` (structured logging)
- [ ] **[TESS-017]** Configure Fastify schema validation: all routes use compiled JSON Schema from the `/schemas` directory. No ad-hoc validation in route handlers.
- [ ] **[TESS-018]** Implement mTLS middleware: Cube API only accepts connections presenting a valid client certificate from the `tesseract-planes` CA. Connections without a valid cert receive `403` before any route logic executes.
- [ ] **[TESS-019]** Implement service account JWT validation: requests must present a JWT signed with `PLANE_TO_CUBE_JWT_SECRET` in the `Authorization: Bearer` header. Validated after mTLS.

#### E1-B: Audit Ledger

- [ ] **[TESS-020]** Implement `AuditLedger` service class in `/cube/src/services/audit-ledger.ts`:
  - Single public method: `append(entry: AuditLedgerEntry): Promise<string>` â€” returns `audit_ledger_entry_id`
  - No `update()`, `delete()`, or `query()` methods on this service
- [ ] **[TESS-021]** Define `AuditLedgerEntry` TypeScript type:
  ```typescript
  type AuditLedgerEntry = {
    packet_id: string;           // UUID â€” from NearMissPacket
    entity_id_hashed: string;
    verdict: 'WATCHLIST' | 'SUSPEND' | 'NEAR_MISS';
    rule_version_applied: string; // Git commit SHA
    input_hash: string;           // SHA-256 of raw NearMissPacket JSON
    evaluation_timestamp: string; // ISO 8601
    remediation_required: boolean;
  };
  ```
- [ ] **[TESS-022]** Implement idempotency check: before writing a new Audit Ledger entry, query for existing `packet_id`. If found, return existing `audit_ledger_entry_id` + original verdict with `already_processed: true`. No duplicate writes.

#### E1-C: API Skeleton

- [ ] **[TESS-023]** Implement `POST /api/v1/cube/evaluate` route:
  - Returns `501 Not Implemented` (stub)
  - Schema validation against `NearMissPacket` schema is active â€” malformed requests return `400` with validation errors
  - Auth middleware (mTLS + JWT) is active
  - Route is logged at `INFO` level via Pino
- [ ] **[TESS-024]** Implement `GET /health` route (unauthenticated):
  - Returns `{ status: "ok", db: "connected" | "error", redis: "connected" | "error" }`
  - Used by Docker Compose `healthcheck`

#### E1-D: Rule Version Control

- [ ] **[TESS-025]** Create initial rule YAML structure in `/rules` repo:
  ```
  /rules
    /v1
      base-edges.yaml       â†’ E1â€“E4 rules
      vertical-edges.yaml   â†’ E5â€“E8 rules
      top-edges.yaml        â†’ E9â€“E12 rules
      aggregation.yaml      â†’ strategy: MAX_SEVERITY (Sprint 0 ratified default)
    manifest.yaml           â†’ lists active rule files + version metadata
  ```
- [ ] **[TESS-026]** Implement rule loader service in `/cube/src/services/rule-loader.ts`:
  - Reads YAML files from the path specified in `CUBE_RULES_PATH` env var
  - Records the Git commit SHA of the loaded rule set at startup
  - Exposes `getRuleVersion(): string` and `getRules(): ParsedRuleSet`
  - Rules are loaded once at startup and cached in memory â€” no hot reload in V1

**Sprint 1 exit gate:** Fastify app starts in Docker. `POST /api/v1/cube/evaluate` returns `400` on malformed input and `501` on valid input. WORM triggers verified. Rule YAML structure committed to `/rules` repo with dual-approval.

---

### SPRINT 2 â€” Risk Tiering Engine
**Duration:** Weeks 3â€“4

#### E1-E: Risk Tiering Engine Implementation

- [ ] **[TESS-027]** Implement `RiskEngine` service in `/cube/src/services/risk-engine.ts`:
  - Input: `NearMissPacket` (validated)
  - Output: `{ verdict: 'WATCHLIST' | 'SUSPEND' | 'NEAR_MISS', remediation_required: boolean, matched_rules: string[] }`
  - Uses `aggregation_strategy: MAX_SEVERITY` â€” evaluates all signals, returns the highest-severity verdict
  - `SUSPEND` > `NEAR_MISS` > `WATCHLIST` in severity order
- [ ] **[TESS-028]** Implement WATCHLIST threshold evaluators (one function per trigger category):
  - [ ] Auth anomalies: â‰¥ 3 failed attempts in 15-minute window
  - [ ] Behavioral deviation: score > 2.5Ïƒ below cohort baseline
  - [ ] Data pattern irregularity: > 15% field validation failures in session
  - [ ] Geographic inconsistency: > 500km location change in 4-hour window
  - [ ] Velocity soft breach: > 80% of permitted limit in 1-hour rolling window
- [ ] **[TESS-029]** Implement SUSPEND threshold evaluators:
  - [ ] Auth failure: â‰¥ 5 consecutive failures
  - [ ] Watchlist recurrence: 3 WATCHLIST verdicts in 72-hour window
  - [ ] Velocity hard breach: > 100% of permitted limit
  - [ ] Prohibited instrument usage: any interaction with restricted list (Edge E7)
  - [ ] Data integrity failure: cross-reference fails against 2+ authoritative sources
  - [ ] Regulatory match: positive match in AML/sanctions source
- [ ] **[TESS-030]** Implement NEAR_MISS threshold evaluators:
  - [ ] Velocity near-breach: â‰¥ 95% and < 100% of permitted limit, self-corrected
  - [ ] Boundary probe: sequence matches known limit-probing pattern
  - [ ] Partial regulatory match: partial match above noise floor, below SUSPEND threshold
  - [ ] Rule gap exposure: signal type not matched by any active rule
  - [ ] Lockdown averted: `DIRECT_ACCESS_ATTEMPT` signal type in payload
- [ ] **[TESS-031]** Wire `RiskEngine` to `POST /api/v1/cube/evaluate` â€” replace `501` stub with full evaluation + Audit Ledger write + response
- [ ] **[TESS-032]** Unit tests: 100% of threshold scenarios covered. Minimum 18 test cases (one per threshold trigger). Use a mock rule set â€” not the production `/rules` YAML.

#### E1-F: Cube Lockdown Protocol

- [ ] **[TESS-033]** Implement `LockdownService` in `/cube/src/services/lockdown.ts`:
  - Subscribes to `tesseract:lockdown` Redis Pub/Sub channel at startup
  - Exposes `triggerLockdown(reason: string): void`
  - On trigger: publishes `CUBE_LOCKDOWN` to Redis Pub/Sub, sets `CUBE_LOCKED` flag in Redis (TTL: none â€” manual clear only), logs at `FATAL` level
- [ ] **[TESS-034]** Implement lockdown detection in API gateway middleware: any request arriving at `POST /api/v1/cube/evaluate` that does not carry a valid Plane mTLS certificate triggers `LockdownService.triggerLockdown()` with reason `DIRECT_ACCESS_ATTEMPT` before returning `403`
- [ ] **[TESS-035]** Implement lockdown state check at route entry: if `CUBE_LOCKED` flag exists in Redis, `POST /api/v1/cube/evaluate` returns `503 Service Unavailable` with body `{ "locked": true, "reason": "CUBE_LOCKDOWN" }` and logs at `WARN` level

#### E1-G: Load Testing & Staging Deploy

- [ ] **[TESS-036]** Load test `POST /api/v1/cube/evaluate` in isolation using `autocannon` or `k6`:
  - 500 req/s sustained for 10 minutes
  - Acceptance: P99 latency < 120ms, zero 5xx errors
- [ ] **[TESS-037]** Deploy Cube to staging Docker environment. Verify `GET /health` returns `200` with all dependencies `"connected"`

**Sprint 2 exit gate:** Cube evaluates all 18+ threshold scenarios correctly in unit tests. Lockdown fires on direct access attempt. Load test passes at 500 req/s P99 < 120ms.

---

## EPIC 2: THE 2D PLANES
### Sprints 3â€“4 | Weeks 5â€“8

---

### SPRINT 3 â€” n8n Infrastructure & Core Workflows
**Duration:** Weeks 5â€“6

#### E2-A: n8n Deployment & Queue Infrastructure

- [ ] **[TESS-038]** Verify n8n is running in Docker Compose, UI accessible at `http://localhost:5678`, persistence verified: create a test workflow, restart container, confirm workflow persists
- [ ] **[TESS-039]** Configure Redis Streams in n8n:
  - Create stream `tesseract:sphere-events` (inbound from Sphere API gateway)
  - Create stream `tesseract:dlq` (Audit Finding 2A dead letter queue)
  - Create consumer group `tesseract-planes` on `tesseract:sphere-events`
  - Configure stream MAXLEN: 10,000 entries (older entries trimmed)
- [ ] **[TESS-040]** Implement message TTL management:
  - n8n workflow runs every 30 seconds
  - Queries `tesseract:sphere-events` for messages older than 120 seconds without consumer acknowledgment
  - Moves expired messages to `tesseract:dlq` with expiry reason `TTL_EXCEEDED`
  - Emits `job_id` status update: `status: "DLQ"` to Sphere notify endpoint
- [ ] **[TESS-041]** Subscribe all Plane consumer workflows to `tesseract:lockdown` Redis Pub/Sub channel. On `CUBE_LOCKDOWN` message: immediately cease dequeuing from `tesseract:sphere-events`, set internal `PLANE_LOCKED` flag, log all in-flight `job_id`s to a `tesseract:lockdown-snapshot` Redis key

#### E2-B: Segmentation-Driven Router

- [ ] **[TESS-042]** Build Segmentation-Driven Router as the master n8n workflow:
  - Trigger: Redis consumer from `tesseract:sphere-events`
  - Step 1: Validate incoming payload against `SegmentationPayload` JSON schema (inline Code node). Malformed payloads â†’ DLQ immediately.
  - Step 2: Read routing ruleset from `ROUTING_RULES_PATH` (versioned JSON file, not hardcoded in workflow)
  - Step 3: Route to correct domain sub-workflow based on `user_tier` + `behavioral_cohort` + `risk_band_last_known`
  - Step 4: Acknowledge Redis Stream message only after successful sub-workflow dispatch
- [ ] **[TESS-043]** Create routing ruleset JSON file `/planes/routing-rules/v1.json` with 10 routing rules covering all combinations of `user_tier` Ã— `risk_band_last_known`:
  - `STANDARD` Ã— `CLEAN` â†’ `standard-onboarding-workflow`
  - `STANDARD` Ã— `WATCHLIST` â†’ `elevated-monitoring-workflow`
  - `ELEVATED` Ã— `CLEAN` â†’ `elevated-onboarding-workflow`
  - `ELEVATED` Ã— `WATCHLIST` â†’ `elevated-monitoring-workflow`
  - `ELEVATED` Ã— `SUSPENDED` â†’ `suspension-review-workflow`
  - `RESTRICTED` Ã— `*` â†’ `restricted-access-workflow`
  - `*` Ã— `UNKNOWN` â†’ `identity-verification-workflow`
  - _(3 additional rules to cover edge combinations)_
- [ ] **[TESS-044]** Build stub domain sub-workflows for each routing target (10 stubs). Each stub: receives payload, logs `job_id` + routed workflow name, returns success. Full implementations in Sprint 4.

#### E2-C: Near Miss Event Emitter

- [ ] **[TESS-045]** Build Near Miss Event Emitter as a reusable n8n sub-workflow (callable from any domain workflow):
  - Input: `{ job_id, entity_id_hashed, risk_signals[], segmentation_context }`
  - Step 1: Construct `NearMissPacket` with `schema_version: "v1.0"`, `packet_id` = UUID (idempotency key), `originating_workflow` = calling workflow ID
  - Step 2: POST to `POST /api/v1/cube/evaluate` with mTLS client cert + service account JWT
  - Step 3: Exponential backoff on failure: 100ms â†’ 200ms â†’ 400ms â†’ 800ms â†’ cap 5s
  - Step 4: On success â€” forward verdict + `job_id` to Sphere notify endpoint (also with backoff per Audit Finding 1C)
  - Step 5: On terminal failure after all retries â€” move original message to DLQ with reason `CUBE_UNREACHABLE`
- [ ] **[TESS-046]** Verify fire-and-forget behavior: the calling domain workflow does not await the Near Miss Emitter. It dispatches and continues. Implement using n8n's `Execute Workflow` node in async mode.

#### E2-D: Plane Self-Diagnostics & DLQ Monitor

- [ ] **[TESS-047]** Build Plane Self-Diagnostics heartbeat workflow:
  - Runs every 60 seconds via n8n Cron trigger
  - Checks: n8n is reachable, Redis Streams `tesseract:sphere-events` consumer lag < 500 messages, `tesseract:dlq` entry count < 50
  - On any check failure: emits `RULE_GAP_EXPOSURE` signal to Near Miss Event Emitter
  - Publishes heartbeat timestamp to Redis key `tesseract:plane-heartbeat`
- [ ] **[TESS-048]** Build DLQ monitor workflow:
  - Polls `tesseract:dlq` every 5 minutes
  - For each DLQ entry with reason `CUBE_UNREACHABLE`: emits a `RULE_GAP_EXPOSURE` Near Miss signal once the Cube is reachable again (implements Audit Finding 2A)
  - For entries with reason `TTL_EXCEEDED`: emits `job_id` status update `status: "DLQ"` to Sphere via `POST /api/sphere/notify`

**Sprint 3 exit gate:** n8n stack running. Router correctly dispatches 10 routing rule types to stub sub-workflows. Near Miss Emitter calls Cube and handles backoff. Heartbeat is running. DLQ receives TTL-expired messages.

---

### SPRINT 4 â€” External Integrations & Full Chain Validation
**Duration:** Weeks 7â€“8

#### E2-E: Google Sheets OAuth2 Configuration

- [ ] **[TESS-049]** In Google Cloud Console:
  - Create new project: `tesseract-planes-integration`
  - Enable Google Sheets API v4
  - Enable Google Drive API (required for Sheets metadata operations)
- [ ] **[TESS-050]** Create OAuth2 credentials â€” **CRITICAL: select `Web Application` type, NOT Desktop Application:**
  - Application type: **Web Application**
  - Authorized redirect URI: `https://[n8n-host]/rest/oauth2-credential/callback`
  - Download client secret JSON. Store `client_id` in `GOOGLE_OAUTH_CLIENT_ID`, `client_secret` in `GOOGLE_OAUTH_CLIENT_SECRET`
  - Document in `/docs/runbooks/google-oauth-setup.md`: the Desktop Application type produces `redirect_uri_mismatch` in production because Google blocks non-`localhost` redirect URIs for Desktop credentials. This credential must be Web Application type.
- [ ] **[TESS-051]** Configure Google Sheets credential in n8n:
  - Navigate to n8n Credentials â†’ New â†’ Google Sheets OAuth2 API
  - Enter `client_id` and `client_secret`
  - Click "Connect" â€” confirm OAuth2 authorization flow completes without `redirect_uri_mismatch` error
  - Confirm token refresh succeeds (test with a 1-hour wait or force-expire the token)

#### E2-F: Google Sheets Sync Bridge Workflow

- [ ] **[TESS-052]** Build Google Sheets Sync Bridge n8n workflow:
  - Trigger: webhook from domain sub-workflows requiring data sync
  - Read operation: `GET` rows from configured sheet ID, filter by entity column
  - Write operation: `APPEND` enriched row to audit sheet (never `UPDATE` â€” append-only to match Audit Ledger philosophy)
  - Rate limit handling: implement 1-second delay between batch operations; on `429` response, retry with 5-second backoff
  - Error handling: on permanent failure, emit DLQ entry + alert
- [ ] **[TESS-053]** Create test Google Sheet with columns: `timestamp`, `entity_id_hashed`, `event_type`, `verdict`, `workflow_id`. Verify bidirectional sync via manual trigger.

#### E2-G: Segmentation Context Injector (Plane-side Validation)

- [ ] **[TESS-054]** Implement Segmentation Context Injector as a reusable n8n Code node (importable by any domain workflow):
  - Validates incoming payload against `SegmentationPayload` JSON Schema v1.0
  - On validation failure: returns structured error `{ valid: false, errors: ValidationError[], job_id }` â€” workflow routes to DLQ
  - On success: enriches payload with `processing_timestamp` and `plane_workflow_id` before forwarding to sub-workflow logic

#### E2-H: Job ID Reconciliation Endpoint (Audit Finding 1A)

- [ ] **[TESS-055]** Implement `GET /api/sphere/verdict/:job_id` reconciliation endpoint in the Sphere API layer (Next.js API route):
  - Queries the Cube's Audit Ledger read replica for the given `job_id` (mapped via `packet_id`)
  - Returns verdict if found, or `{ status: "PENDING" }` if not yet evaluated, or `{ status: "DLQ", reason: string }` if in dead letter queue
  - This endpoint is read-only and does not trigger any Cube evaluation

#### E2-I: End-to-End Integration Test

- [ ] **[TESS-056]** Write integration test script (`/planes/tests/e2e-chain-test.ts`):
  - Sends 5 mock `SegmentationPayload` events to the Sphere API gateway mock
  - Verifies each event: dequeued from Redis â†’ routed by Segmentation Router â†’ Near Miss Emitter fires â†’ Cube evaluates â†’ Audit Ledger entry written â†’ Sphere receives WebSocket verdict push
  - Verifies `job_id` is consistent across all hops
  - Verifies DLQ workflow: send a malformed payload, confirm it lands in `tesseract:dlq` within TTL window
- [ ] **[TESS-057]** Security review of all n8n webhook endpoints:
  - All inbound n8n webhooks require `Authorization: Bearer [SPHERE_BEARER_TOKEN_SECRET]` header
  - n8n is not publicly accessible â€” only reachable from within Docker internal network or via API gateway
  - Confirm: no n8n webhook responds to unauthenticated requests

**Sprint 4 exit gate:** Google Sheets OAuth2 authorized as Web Application without errors. Full chain integration test passes (5/5 events). Reconciliation endpoint returns correct state. DLQ correctly receives malformed payloads.

---

## EPIC 3: THE OUTER SPHERE
### Sprints 5â€“6 | Weeks 9â€“12

---

### SPRINT 5 â€” Multi-Agent AI Layer & API Gateway
**Duration:** Weeks 9â€“10

#### E3-A: Next.js Scaffold & API Gateway

- [ ] **[TESS-058]** Scaffold Next.js 15 App Router application in `/sphere`:
  ```
  /sphere
    /app
      /api
        /gateway/v1/route.ts     â†’ Sphere inbound endpoint (enqueues to Redis)
        /sphere/notify/route.ts  â†’ Plane â†’ Sphere verdict push endpoint
        /sphere/verdict/[job_id]/route.ts â†’ Reconciliation endpoint (Audit Finding 1A)
        /health/route.ts
      /dashboard                 â†’ Sphere Health Monitor (operator-only)
      /layout.tsx
      /page.tsx
    /components
      /antigravity               â†’ Bento Grid layout engine
      /verdicts                  â†’ Verdict UI components
    /lib
      /agents                    â†’ AI agent definitions
      /ws                        â†’ WebSocket client
      /store                     â†’ job_id registry (Zustand)
  ```
- [ ] **[TESS-059]** Implement `POST /api/gateway/v1` route:
  - Validates `Authorization: Bearer` token
  - Constructs `SegmentationPayload` skeleton from session context
  - Generates `job_id` (UUID)
  - Enqueues to `tesseract:sphere-events` Redis Stream
  - Returns `202 Accepted` with patched schema: `{ job_id, status: "QUEUED", ttl_seconds: 120, poll_endpoint: "/api/sphere/verdict/{job_id}" }`
- [ ] **[TESS-060]** Implement `POST /api/sphere/notify` route:
  - Receives Plane verdict push `{ job_id, verdict, context }`
  - Validates Plane service account JWT
  - Pushes verdict to per-session WebSocket channel
  - Updates `job_id` status in Redis: `status: "VERDICT_RECEIVED"`
- [ ] **[TESS-061]** Implement API Gateway hard-block: any request attempting to reach the Cube directly (i.e., routing to `CUBE_PORT` or containing `cube` in path) is blocked at the Next.js middleware layer. This generates a `DIRECT_ACCESS_ATTEMPT` risk signal (logged and forwarded to Plane for Cube evaluation).

#### E3-B: Multi-Agent AI Topology

- [ ] **[TESS-062]** Define agent topology in `/sphere/lib/agents/topology.ts`:
  - **Orchestrator Agent** (Claude Sonnet 4.6): receives raw user intent, classifies intent into one of 20 defined `IntentType` values, constructs `SegmentationPayload`, dispatches to `POST /api/gateway/v1`
  - **Classification Agents** (Claude Haiku 4.5): high-volume, narrow tasks â€” fraud signal tagging, entity type detection, cohort assignment. Run in parallel, feed structured tags back to Orchestrator before SegmentationPayload construction.
- [ ] **[TESS-063]** Implement Orchestrator Agent using Anthropic SDK with structured output:
  ```typescript
  // Orchestrator must produce this exact output shape
  type OrchestratorOutput = {
    intent_type: IntentType;            // one of 20 defined values
    segmentation_payload: SegmentationPayload;
    classification_tags: ClassificationTag[];
    routing_confidence: number;         // 0.0â€“1.0
  };
  ```
  - Enable prompt caching on the system prompt (Anthropic SDK `cache_control: { type: "ephemeral" }`) â€” the system prompt contains the 20 `IntentType` definitions and is re-used across all requests
- [ ] **[TESS-064]** Implement Classification Agents (Haiku 4.5):
  - `FraudSignalAgent`: tags incoming session data with fraud indicators
  - `EntityTypeAgent`: classifies entity as individual/business/institutional
  - `CohortAgent`: assigns behavioral cohort label based on session history
  - All three run in parallel via `Promise.all()` â€” Orchestrator awaits all three before constructing SegmentationPayload
- [ ] **[TESS-065]** Implement `job_id` registry in Zustand store (`/sphere/lib/store/job-registry.ts`):
  - Stores: `{ job_id, status, submitted_at, verdict? }`
  - On WebSocket verdict push: update `status` to `VERDICT_RECEIVED`, store `verdict`
  - Background timer: every 5 seconds, check all entries with `status: "QUEUED" | "PROCESSING"` older than 30 seconds â†’ set `status: "PROCESSING_TIMEOUT"` â†’ call `GET /api/sphere/verdict/:job_id` reconciliation endpoint (Audit Finding 1B)

#### E3-C: WebSocket & Sphere Health Monitor

- [ ] **[TESS-066]** Implement WebSocket client in `/sphere/lib/ws/client.ts`:
  - Connects to per-session verdict channel on mount
  - On disconnect: immediately attempt reconnect (max 5 retries, exponential backoff)
  - On reconnect: iterate all `QUEUED`/`PROCESSING` entries in `job_id` registry and call reconciliation endpoint for each
- [ ] **[TESS-067]** Implement Sphere Health Monitor WebSocket feed:
  - Server-side: Next.js route streams real-time metrics from Redis every 1 second: `{ active_agents, p50_ms, p95_ms, queue_depth, dlq_depth }`
  - Client-side: operator-only dashboard at `/dashboard` renders live gauges using the metrics stream

#### E3-D: Stress Test

- [ ] **[TESS-068]** Stress test full Sphere â†’ Plane â†’ Cube chain:
  - 1,000 concurrent simulated users using `k6`
  - Each user: submits 1 event per second for 5 minutes
  - Acceptance criteria:
    - P99 latency for `POST /api/gateway/v1` < 200ms (includes AI agent processing)
    - P99 latency for WebSocket verdict push < 500ms from event submission
    - No P99 regression > 15% vs. Phase 2 (Plane-only) baseline
    - Zero `CUBE_LOCKDOWN` events
    - DLQ depth < 10 entries throughout test

**Sprint 5 exit gate:** Orchestrator Agent correctly classifies 20/20 intent types. WebSocket verdict push works end-to-end. Reconciliation endpoint returns correct `job_id` state. Stress test passes.

---

### SPRINT 6 â€” Antigravity Frontend & MVC Hardening
**Duration:** Weeks 11â€“12

#### E3-E: Antigravity Bento Grid Layout Engine

- [ ] **[TESS-069]** Implement `AntigravityGrid` layout engine in `/sphere/components/antigravity/grid.tsx`:
  - Uses CSS Grid with dynamic column/row assignment computed at render time
  - No component has a hardcoded `gridColumn` or `gridRow` prop â€” all positions are computed from `semantic_weight`
  - Components declare `semantic_weight_class: keyof typeof SEMANTIC_WEIGHT_MAP` only
  - Layout recomputes on: viewport resize, new component mount, semantic weight change
- [ ] **[TESS-070]** Implement `SEMANTIC_WEIGHT_MAP` as defined in Tech Stack Blueprint. Verify visual gravity test: mount a `CUBE_ORIGINATED_HIGH` component alongside `SPHERE_NATIVE` components â€” `CUBE_ORIGINATED_HIGH` must occupy top-left, maximum-scale position within 200ms of mount
- [ ] **[TESS-071]** Implement Framer Motion spring animations for all Antigravity components:
  - Stiffness: 300, Damping: 30 (reflects damping metaphor in system architecture)
  - All position and scale changes use `layout` animation prop â€” never `transition: { type: "tween" }`
- [ ] **[TESS-072]** Build 8 core component types for the Bento Grid:
  - [ ] `VerdictCard` â€” displays Cube verdict with semantic weight class
  - [ ] `AgentStatusTile` â€” displays AI agent activity
  - [ ] `QueueDepthGauge` â€” live Redis queue depth
  - [ ] `SegmentationBadge` â€” user tier + cohort display
  - [ ] `JobStatusTracker` â€” real-time `job_id` status from Zustand store
  - [ ] `ProcessingTimeoutAlert` â€” surfaced on `PROCESSING_TIMEOUT` state (Audit Finding 1B)
  - [ ] `DQLEntryNotice` â€” surfaced when `job_id` enters DLQ state (Audit Finding 2C)
  - [ ] `SystemHealthBanner` â€” Sphere Health Monitor summary (operator-only)
- [ ] **[TESS-073]** Verify 8 components render correctly across 4 viewport breakpoints: 375px (mobile), 768px (tablet), 1280px (desktop), 1920px (wide)

#### E3-F: UI Wiring to AI Layer

- [ ] **[TESS-074]** Wire all user-initiated UI actions through the Orchestrator Agent:
  - Zero direct calls from UI components to `POST /api/gateway/v1` â€” all UI actions dispatch to a `useAgent()` hook that calls the Orchestrator
  - The Orchestrator constructs the SegmentationPayload and dispatches to the gateway
  - UI components receive state updates only from the Zustand `job_id` registry â€” never from direct API responses
- [ ] **[TESS-075]** Implement `useAgent()` hook:
  - Accepts: `{ user_intent: string, context: Partial<SegmentationPayload> }`
  - Returns: `{ submit: () => Promise<string>, job_id: string | null, status: JobStatus }`
  - Internally: calls Orchestrator Agent â†’ dispatches to gateway â†’ registers `job_id` in Zustand store

#### E3-G: MVC Acceptance Tests

- [ ] **[TESS-076]** Full end-to-end MVC acceptance test suite (`/sphere/tests/mvc-acceptance.test.ts`):
  - [ ] WATCHLIST scenario: submit event triggering auth anomaly â†’ verify verdict surfaced in `VerdictCard` with `CUBE_ORIGINATED_MEDIUM` weight
  - [ ] SUSPEND scenario: submit event triggering 5 consecutive auth failures â†’ verify verdict surfaced with `CUBE_ORIGINATED_HIGH` weight, session terminated
  - [ ] NEAR_MISS scenario: submit event at 96% velocity threshold â†’ verify `VerdictCard` appears, `JobStatusTracker` shows `VERDICT_RECEIVED`
  - [ ] DLQ scenario: submit malformed payload â†’ verify `DQLEntryNotice` surfaces after TTL expiry
  - [ ] Timeout scenario: simulate WebSocket disconnect during processing â†’ verify `ProcessingTimeoutAlert` surfaces after 30 seconds â†’ reconnect â†’ verify reconciliation endpoint restores verdict
  - [ ] Lockdown scenario: simulate direct Sphere-to-Cube access attempt â†’ verify `CUBE_LOCKDOWN` broadcast received â†’ verify all Planes halt â†’ verify Sphere enters maintenance state

#### E3-H: Security Penetration Test

- [ ] **[TESS-077]** Security penetration test checklist:
  - [ ] Direct Sphere-to-Cube HTTP call â†’ confirm `403` + `CUBE_LOCKDOWN` fires
  - [ ] Malformed NearMissPacket injection (missing `packet_id`) â†’ confirm `400` from Cube schema validation
  - [ ] Duplicate `packet_id` replay â†’ confirm `already_processed: true` returned, no second Audit Ledger write
  - [ ] Expired JWT on Plane-to-Cube call â†’ confirm `401` from Cube JWT middleware
  - [ ] OAuth2 token replay (Google Sheets) â†’ confirm token rotation invalidates replayed token
  - [ ] SQL injection attempt via `entity_id_hashed` field â†’ confirm parameterized query prevents injection
  - [ ] XSS via `behavioral_cohort` field rendered in UI â†’ confirm Next.js escaping prevents execution

#### E3-I: Runbook Documentation

- [ ] **[TESS-078]** Write `/docs/runbooks/cube-lockdown-recovery.md`:
  - Step 1: Identify lockdown trigger from Audit Ledger query
  - Step 2: Clear `CUBE_LOCKED` flag in Redis (requires 2-person authorization)
  - Step 3: Verify no active direct-access vectors remain
  - Step 4: Resume Plane consumer groups from `tesseract:sphere-events`
  - Step 5: Verify Sphere WebSocket connections re-establish
- [ ] **[TESS-079]** Write `/docs/runbooks/n8n-workflow-failure-recovery.md`:
  - DLQ triage procedure
  - Manual re-queue from `tesseract:dlq` to `tesseract:sphere-events`
  - Fallback workflow activation procedure
- [ ] **[TESS-080]** Write `/docs/runbooks/google-oauth-token-refresh-failure.md`:
  - Symptoms: n8n Google Sheets nodes return `401 Unauthorized`
  - Resolution: Re-authorize OAuth2 credential in n8n (credential must remain Web Application type)
  - Prevention: Monitor token expiry; n8n auto-refresh should prevent this in normal operation

**Sprint 6 exit gate (MVC Definition of Done):**
All 6 acceptance test scenarios pass. All 7 security pen test checks pass. All 3 runbooks merged to `/docs`. A user interaction in the Antigravity UI flows through the Orchestrator Agent â†’ n8n Plane â†’ Cube evaluation â†’ WebSocket verdict push â†’ `VerdictCard` in Bento Grid, with the full chain auditable in the Audit Ledger.

---

## TICKET SUMMARY BY EPIC

| Epic | Sprint | Ticket Range | Count |
|---|---|---|---|
| **E0: Environment** | Sprint 0 | TESS-000 â†’ TESS-014 | 15 tickets |
| **E1: Inner Cube** | Sprints 1â€“2 | TESS-015 â†’ TESS-037 | 23 tickets |
| **E2: 2D Planes** | Sprints 3â€“4 | TESS-038 â†’ TESS-057 | 20 tickets |
| **E3: Outer Sphere** | Sprints 5â€“6 | TESS-058 â†’ TESS-080 | 23 tickets |
| **TOTAL** | | **TESS-000 â†’ TESS-080** | **81 tickets** |

---

## DEPENDENCY MAP

```
TESS-000 â†’ TESS-003 (repo structure before anything)
TESS-004 â†’ TESS-009 (Docker before all services)
TESS-010 â†’ TESS-014 (schemas before Sprint 1 implementation)
TESS-015 â†’ TESS-019 (Fastify scaffold before all Cube features)
TESS-020 â†’ TESS-022 (Audit Ledger before Risk Engine)
TESS-027 â†’ TESS-035 (Risk Engine before Lockdown wiring)
TESS-036 â†’ TESS-037 (tests + deploy before Plane integration)
TESS-038 â†’ TESS-041 (n8n + queue before workflows)
TESS-042 â†’ TESS-044 (Router before domain workflows)
TESS-049 â†’ TESS-051 (OAuth2 config before Sheets workflow)
TESS-055 (reconciliation endpoint) â†’ required by TESS-065 (job_id registry timeout)
TESS-056 â†’ TESS-057 (e2e test before security review)
TESS-058 â†’ TESS-061 (Next.js scaffold + gateway before AI layer)
TESS-062 â†’ TESS-065 (Agents before Zustand store)
TESS-069 â†’ TESS-075 (Grid before acceptance tests)
TESS-076 (acceptance) â†’ TESS-077 (pen test) â†’ TESS-078â€“080 (runbooks)
```

---

# PART 3: HOLDING PATTERN CONFIRMATION

Architecture audit complete. Execution plan complete. **I am not writing any application code, n8n JSON workflows, or Next.js components.**

Awaiting your explicit approval on the following before initiating the codebase:

1. **Audit findings accepted?** Confirm the 5 patches (F1A/B/C, F2A/B/C, F3A/B/C) are approved for integration into the PRD before Sprint 1 begins.
2. **81-ticket plan approved?** Confirm the ticket structure, Epic breakdown, and Sprint 0 pre-work are acceptable as the source of truth.
3. **Sprint 0 start authorized?** Sprint 0 is infrastructure-only (Docker, schema ratification, repo setup) â€” no application logic. Confirm whether to proceed here first, or jump straight to Sprint 1 once approved.

Ready on your signal.
