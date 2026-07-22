# PROJECT TESSERACT: THE FRACTAL-STATE ENGINE
### Complete Architecture Package — V1 Prototype

---

# DELIVERABLE 1: PRODUCT REQUIREMENTS DOCUMENT (PRD)

---

## EXECUTIVE SUMMARY

**Product:** Project Tesseract — The Fractal-State Engine  
**Classification:** V1 Prototype (Minimum Viable Cube)  
**Version:** 0.9 — Internal Architecture Draft  
**Date:** 2026-06-08  

---

> *"Rigid systems do not fail gradually — they snap. Tesseract is engineered on the principle that true resilience is not hardness, but the disciplined orchestration of fluid, semi-rigid, and immutable states in topological sequence."*

Project Tesseract is an AI-augmented, compliance-hardened platform built on a **Dual-Core Damping** topology. Unlike conventional three-tier architectures that treat all layers as interchangeable, Tesseract enforces a strict material-science analogy: each layer has a defined **state of matter**, a defined **response to pressure**, and a defined **failure mode**. The system is designed such that external chaos is absorbed, filtered, and neutralized before it ever reaches the immutable compliance core.

The three operational layers are:

| Layer | Metaphysical State | Engineering Equivalent | Failure Mode |
|---|---|---|---|
| The Outer Sphere | Liquid | AI-Driven UI / API Gateway | Deforms without breaking |
| The 2D Damping Planes | Phase Transition | n8n Workflow Engine / Business Logic | Restructures under load |
| The Inner Cube | Solid | Compliance & Risk Engine | Locks down — never bends |

---

## PROBLEM STATEMENT

### The Brittleness Problem in Modern Platforms

Contemporary enterprise platforms are architected as monolithic rigid stacks. When external load — whether from user volume, adversarial input, regulatory edge cases, or market volatility — exceeds a threshold, these systems do not deform gracefully. **They fracture.** The failure is catastrophic and binary.

Specifically, the pathologies addressed by Tesseract include:

- **Compliance engines interrogated in real-time by UI layers**, creating latency spikes and brittle coupling that breaks under load.
- **Business logic hardcoded into front-end routing**, meaning a single rule change requires a full deployment cycle.
- **Risk systems using traffic-light metaphors** (Red/Amber/Green) that are semantically imprecise, creating ambiguity in escalation workflows.
- **Automation pipelines that are monolithic scripts** rather than modular, re-addressable nodes — creating fragile single points of failure.
- **OAuth2 misconfiguration in data-sync integrations** — most critically, configuring external APIs (e.g., Google Sheets) as Desktop Application flows, which causes redirect URI mismatch failures in production web deployments.

### The Tesseract Solution: Liquid-to-Solid Buffering

The Fractal-State Engine solves brittleness through **topological damping**. Every unit of external pressure entering the Outer Sphere is absorbed, reshaped, and classified before it reaches the Inner Cube. The Cube itself *never receives raw external input* — it only receives pre-filtered, validated, segmentation-tagged events from the 2D Planes. This architecture guarantees:

1. The UI (Sphere) can be infinitely fluid and experimental without destabilizing compliance.
2. The business logic (Planes) can restructure itself dynamically without touching core rules.
3. The Cube enforces absolute law — immutable, auditable, non-negotiable.

---

## CORE FEATURES — MAPPED TO THE THREE LAYERS

---

### LAYER 1: THE OUTER SPHERE
**State:** Liquid | **Responsibility:** UX, AI Routing, External Interface

The Sphere is the product's surface tension. It must handle infinite variability without transmitting structural pressure inward.

| Feature ID | Feature Name | Description |
|---|---|---|
| `SPH-001` | **Antigravity Bento Grid** | Modular UI layout engine. Components float independently in a 2D grid with configurable gravity vectors. No component has a fixed parent — layout is computed at render time based on available viewport and user-segment context. |
| `SPH-002` | **Multi-Agent AI Routing Layer** | An ensemble of specialized AI agents (Claude Sonnet 4.6 / Haiku 4.5 for speed) that intercept all user intent and route it to the correct 2D Plane workflow. No user action reaches the Cube directly. |
| `SPH-003` | **Segmentation Context Injector** | Every API call from the Sphere is enriched with a `SegmentationPayload` — a structured JSON envelope containing user tier, behavioral cohort, risk band (read-only from Cube), and session state. |
| `SPH-004` | **Organic Interaction Surfaces** | All UI components use physics-based animation (spring curves, not easing functions). Transitions are non-linear, reflecting the fluid-state metaphor. |
| `SPH-005` | **Sphere Health Monitor** | Real-time WebSocket dashboard displaying active agent count, routing latency P50/P95, and 2D Plane queue depth. Visible only to operators. |

**Antigravity Design Principles — Formal Definition:**

> Components in the Antigravity system have no fixed Z-axis. They occupy space proportional to their semantic weight, not their pixel dimensions. A compliance alert from the Cube will visually "rise" to prominence — not because it is programmatically positioned first, but because its semantic weight class is `CUBE_ORIGINATED: HIGH`, which the layout engine resolves to maximum visual gravity.

---

### LAYER 2: THE 2D DAMPING PLANES
**State:** Phase-Transitional | **Responsibility:** Business Logic, Automation, API Bridges

The Planes are the friction layer. They are densely connected, self-reorganizing, and powered entirely by n8n automation pipelines. Their single contractual obligation to the architecture is: *they must reduce high-entropy Sphere events into low-entropy, structured Cube-ready signals.*

| Feature ID | Feature Name | Description |
|---|---|---|
| `PLN-001` | **n8n Workflow Mesh** | A network of modular n8n workflows, each handling a single domain (user onboarding, transaction validation, data enrichment, alert dispatch). No workflow has more than 3 external dependencies. |
| `PLN-002` | **Segmentation-Driven Router** | The master n8n orchestration workflow. It reads the `SegmentationPayload` from the Sphere and routes the event to the correct domain workflow. Routing logic is stored as a versioned JSON ruleset — not hardcoded in the workflow graph. |
| `PLN-003` | **Google Sheets Sync Bridge** | A dedicated n8n workflow that performs bidirectional sync with Google Sheets via the Sheets API v4. **Authentication is strictly OAuth2 configured as a Web Application** — Client ID and Client Secret are issued against the Web Application credential type, with an explicit redirect URI (`https://[n8n-host]/rest/oauth2-credential/callback`) registered in Google Cloud Console to prevent redirect URI mismatch errors in production. |
| `PLN-004` | **Near Miss Event Emitter** | A sub-workflow triggered by any risk signal. It packages the event into a `NearMissPacket` and dispatches it to the Cube's event ingestion endpoint via an async, fire-and-forget HTTP call with exponential backoff. The Sphere is never blocked waiting for this call to resolve. |
| `PLN-005` | **Shock Absorption Queue** | A Redis-backed message queue that sits between the Sphere API gateway and the n8n webhook triggers. Under load, the Planes accept work from the queue at their own pace — the Sphere never experiences back-pressure from Plane latency. |
| `PLN-006` | **Plane Self-Diagnostics** | Each n8n workflow emits a heartbeat to a central monitoring topic. If a workflow fails to heartbeat within its configured SLA window, the Segmentation Router automatically falls back to a pre-configured safe-path workflow for that domain. |

---

### LAYER 3: THE INNER CUBE
**State:** Solid | **Responsibility:** Compliance Engine, Risk Tiering, Immutable Rules

The Cube does not negotiate. It does not accept UI events. It does not make exceptions. It processes only validated, Plane-originated signals and responds with exactly one of three verdicts.

**The 12 Edges — Rigid Protocol Locks:**

The Cube's architecture maps to the 12 edges of a geometric cube. Each edge represents an immutable protocol boundary:

| Edge Group | Edges (4 per group) | Protocol Domain |
|---|---|---|
| **Base Edges** | E1–E4 | Identity Verification, KYC/AML Baseline, Session Integrity, Data Provenance |
| **Vertical Edges** | E5–E8 | Transaction Limits, Velocity Rules, Geographic Restrictions, Instrument Eligibility |
| **Top Edges** | E9–E12 | Regulatory Reporting Triggers, Audit Trail Immutability, Escalation Paths, Cube Lockdown Conditions |

| Feature ID | Feature Name | Description |
|---|---|---|
| `CUB-001` | **Risk Tiering Engine** | Evaluates all incoming Plane signals against the 12 Edge protocols. Emits exactly one of three verdicts: `WATCHLIST`, `SUSPEND`, or `NEAR_MISS`. No other verdicts exist. The traffic-light system is explicitly prohibited. |
| `CUB-002` | **Immutable Audit Ledger** | Append-only event store. Every Cube decision is written with a cryptographic hash of the input signal, the rule version applied, the timestamp, and the verdict. No record can be amended post-write. |
| `CUB-003` | **Cube Lockdown Protocol** | If the Sphere is breached (i.e., an unvalidated signal reaches the Cube directly), all 12 edges lock simultaneously. All Plane workflows receive a `CUBE_LOCKDOWN` broadcast and cease processing. The Sphere goes to a static maintenance state. |
| `CUB-004` | **Rule Version Control** | All Cube rules are stored as versioned, signed YAML files in a Git repository. New rule versions require a dual-approval merge before deployment. Rollback is instant. |
| `CUB-005` | **Cube API — Inbound Only** | The Cube exposes a single inbound REST endpoint: `POST /api/v1/cube/evaluate`. It accepts only `NearMissPacket` structures from authenticated Plane services. It has zero outbound API calls — all responses are returned synchronously to the calling Plane. |

---

## STRICT COMPLIANCE METRICS — RISK TIER DEFINITIONS

The following thresholds are non-negotiable. They are codified in the Cube's YAML ruleset and cannot be modified without a dual-approval Git merge.

### WATCHLIST
> *The entity remains active but is flagged for heightened monitoring. No operational restriction is applied. All subsequent actions from this entity are logged at `VERBOSE` level and reviewed within 24 hours.*

| Trigger Category | Threshold |
|---|---|
| Authentication anomalies | ≥ 3 failed attempts within a 15-minute window |
| Behavioral deviation | Session behavior score drops > 2.5σ below cohort baseline |
| Data pattern irregularity | > 15% of submitted data fields fail format validation in a single session |
| Geographic inconsistency | Login location change > 500km within a 4-hour window without pre-authorization |
| Velocity soft breach | Transaction velocity exceeds 80% of permitted limit over a 1-hour rolling window |

### SUSPEND
> *The entity's operational access is immediately suspended. All active sessions are terminated. The entity must complete a re-verification workflow before access is restored. This verdict is automatically escalated to the compliance officer queue.*

| Trigger Category | Threshold |
|---|---|
| Authentication failure | ≥ 5 consecutive failed authentication attempts |
| Watchlist recurrence | Entity receives 3 WATCHLIST verdicts within any 72-hour window |
| Velocity hard breach | Transaction velocity exceeds 100% of permitted limit |
| Prohibited instrument usage | Any attempt to interact with an instrument on the restricted list (Edge E7) |
| Data integrity failure | Submitted identity data fails cross-reference verification against 2+ authoritative sources |
| Regulatory match | Entity name or associated identifiers produce a positive match in any AML/sanctions screening source |

### NEAR MISS
> *A critical compliance event that did not result in a breach, but came within the defined tolerance envelope of a prohibited outcome. This verdict is the most important operationally — it signals that the system's damping layers functioned correctly but were stressed. Near Miss events trigger a mandatory post-mortem review within 48 hours and may result in rule recalibration.*

| Trigger Category | Threshold |
|---|---|
| Velocity near-breach | Transaction velocity reached ≥ 95% but < 100% of permitted limit and self-corrected |
| Boundary probe detected | A sequence of actions that algorithmically maps to a known limit-probing pattern without crossing the limit |
| Partial regulatory match | Entity identifiers produce a partial (non-conclusive) match in screening sources — insufficient for SUSPEND but above noise floor |
| Rule gap exposure | A Plane workflow routes a signal to the Cube that does not map to any existing rule — the Cube processes it safely, but the gap itself is the Near Miss event |
| Lockdown averted | A direct Sphere-to-Cube signal is detected and blocked by the API gateway — classified as Near Miss since the architectural invariant was *attempted* to be violated |

---
---

# DELIVERABLE 2: STRATEGIC PROGRESS PLAN — 12-WEEK AGILE ROADMAP

---

**Methodology:** Scrum with 2-week sprints (6 sprints total)  
**Target:** Minimum Viable Cube (MVC) — all three layers operational in integration

---

## PHASE 1: FORGING THE CUBE (Weeks 1–4)

> *Build the immutable core first. Nothing else can be validated until the compliance engine exists and is testable.*

### Sprint 1 — Weeks 1–2: Cube Foundation

| Task ID | Task | Owner | Acceptance Criteria |
|---|---|---|---|
| `S1-01` | Design and ratify the 12 Edge protocol YAML schema | Architect + Compliance Lead | Schema reviewed, signed, merged to `main` |
| `S1-02` | Stand up the append-only Audit Ledger (PostgreSQL with WORM policy) | Backend Lead | Writes succeed; no UPDATE/DELETE permitted at DB level |
| `S1-03` | Implement `POST /api/v1/cube/evaluate` inbound endpoint skeleton | Backend | Returns 501 stub; auth middleware in place |
| `S1-04` | Define `NearMissPacket` JSON schema (OpenAPI 3.1) | Architect | Schema published to internal API registry |
| `S1-05` | Initialize Rule Version Control repository with dual-approval branch protection | DevOps | PR to `rules/main` requires 2 approvals; signed commits enforced |

### Sprint 2 — Weeks 3–4: Risk Tiering Engine

| Task ID | Task | Owner | Acceptance Criteria |
|---|---|---|---|
| `S2-01` | Implement Risk Tiering Engine — WATCHLIST, SUSPEND, NEAR_MISS verdict logic | Backend | 100% of defined threshold scenarios covered by unit tests |
| `S2-02` | Wire Risk Engine to `POST /api/v1/cube/evaluate` endpoint | Backend | Integration test: valid NearMissPacket returns correct verdict |
| `S2-03` | Implement Cube Lockdown Protocol (Edge E9–E12 group) | Backend | Lockdown broadcast fires on direct Sphere-to-Cube signal detection |
| `S2-04` | Load test the Cube endpoint in isolation | QA | P99 latency < 120ms at 500 req/s sustained for 10 minutes |
| `S2-05` | Deploy Cube to staging environment | DevOps | Cube endpoint live and reachable from staging n8n instance |

**Phase 1 Exit Criteria:** The Inner Cube accepts a valid NearMissPacket, applies the correct risk tier verdict, writes to the Audit Ledger, and returns a structured response — all within the defined latency budget.

---

## PHASE 2: THE 2D CONNECTORS (Weeks 5–8)

> *Build the n8n mesh. Wire the Planes to the Cube. Establish the Segmentation-Driven routing logic and all external data bridges.*

### Sprint 3 — Weeks 5–6: n8n Infrastructure & Core Workflows

| Task ID | Task | Owner | Acceptance Criteria |
|---|---|---|---|
| `S3-01` | Deploy self-hosted n8n instance to staging (Docker Compose + persistent volume) | DevOps | n8n UI accessible; workflow persistence verified across restart |
| `S3-02` | Implement Shock Absorption Queue (Redis + n8n webhook triggers) | Backend | Queue depth visible in monitoring; Plane processes from queue asynchronously |
| `S3-03` | Build Segmentation-Driven Router workflow (master n8n orchestrator) | Automation Lead | Routes 10 pre-defined SegmentationPayload types to correct domain stubs |
| `S3-04` | Build Near Miss Event Emitter sub-workflow | Automation Lead | Fire-and-forget POST to Cube with exponential backoff on failure; Sphere never blocked |
| `S3-05` | Implement Plane Self-Diagnostics heartbeat system | Automation Lead | Missing heartbeat triggers fallback route within configured SLA window |

### Sprint 4 — Weeks 7–8: External Integrations & Google Sheets Bridge

| Task ID | Task | Owner | Acceptance Criteria |
|---|---|---|---|
| `S4-01` | **Configure Google Sheets OAuth2 (Web Application)** — Create project in Google Cloud Console, enable Sheets API v4, create OAuth2 credential of type **Web Application** (not Desktop), register redirect URI `https://[n8n-host]/rest/oauth2-credential/callback` explicitly | DevOps + Automation Lead | OAuth2 authorization flow completes without redirect URI mismatch; token refresh succeeds |
| `S4-02` | Build Google Sheets Sync Bridge n8n workflow (bidirectional read/write) | Automation Lead | Workflow reads from target Sheet, writes enriched row, and handles rate-limit backoff |
| `S4-03` | Implement Segmentation Context Injector — all Plane workflow inputs validated against SegmentationPayload schema | Automation Lead | Workflow rejects malformed payloads with structured error; valid payloads proceed |
| `S4-04` | End-to-end integration test: Sphere mock → Queue → Plane → Near Miss Emitter → Cube → Audit Ledger | QA | Full chain executes; Audit Ledger entry verifiable; latency budget met |
| `S4-05` | Security review of all n8n webhook endpoints (token auth, IP allowlist) | Security | All endpoints require Bearer token; only Sphere API gateway IP whitelisted |

> **Critical Note on `S4-01` — OAuth2 Web Application Configuration:**  
> The Google Sheets integration **must** use the **Web Application** credential type in Google Cloud Console. Using the **Desktop Application** type in a server-deployed n8n instance will result in a `redirect_uri_mismatch` error because Google rejects non-`localhost` redirect URIs for Desktop credentials. The n8n OAuth2 callback URL is a server-side redirect — it must be registered as a Web Application with the full production callback URI. This is a non-recoverable configuration error if deployed incorrectly; fix it at the credential creation step, not after.

**Phase 2 Exit Criteria:** The n8n Plane mesh accepts events from a mock Sphere, routes them via segmentation logic, emits Near Miss packets to the Cube, and syncs data through the Google Sheets bridge — all without the Cube being directly accessible from outside the Plane network.

---

## PHASE 3: INFLATING THE SPHERE (Weeks 9–12)

> *Deploy the AI routing layer and the Antigravity frontend. The Sphere wraps around a fully operational Cube and Plane mesh.*

### Sprint 5 — Weeks 9–10: Multi-Agent AI Layer

| Task ID | Task | Owner | Acceptance Criteria |
|---|---|---|---|
| `S5-01` | Design multi-agent topology: Orchestrator Agent + Domain Specialist Agents (Claude Sonnet 4.6 for routing; Haiku 4.5 for high-volume classification) | AI Lead | Agent responsibility matrix documented and approved |
| `S5-02` | Implement Orchestrator Agent — receives user intent, constructs SegmentationPayload, dispatches to Plane queue | AI Lead | Orchestrator correctly classifies 20 predefined intent types; dispatches to correct queue topic |
| `S5-03` | Implement Sphere Health Monitor WebSocket feed | Backend | Real-time metrics stream: agent count, routing latency P50/P95, queue depth |
| `S5-04` | Build API Gateway layer (rate limiting, auth, Sphere-to-Plane-only routing enforcement) | Backend | Direct Sphere-to-Cube calls blocked at gateway; logged as Near Miss candidate |
| `S5-05` | Stress test: 1,000 concurrent simulated users against full Sphere → Plane → Cube chain | QA | No P99 latency regression > 15% vs. Phase 2 baseline; zero Cube lockdown events |

### Sprint 6 — Weeks 11–12: Antigravity Frontend & MVC Hardening

| Task ID | Task | Owner | Acceptance Criteria |
|---|---|---|---|
| `S6-01` | Implement Antigravity Bento Grid layout engine (React + Framer Motion spring physics) | Frontend Lead | 8 core component types render correctly across 4 viewport breakpoints |
| `S6-02` | Wire UI components to AI Routing Layer — all user actions dispatch through Orchestrator Agent | Frontend + AI Lead | Zero direct backend calls from UI; all traffic through agent layer |
| `S6-03` | Implement semantic weight class system for Cube-originated alerts (`CUBE_ORIGINATED: HIGH` rises to visual prominence automatically) | Frontend | Visual gravity test: Cube alert appears above all other content within 200ms of verdict receipt |
| `S6-04` | Full end-to-end MVC acceptance test suite | QA | All three layers operational; 100% of WATCHLIST/SUSPEND/NEAR_MISS scenarios produce correct UI state |
| `S6-05` | Security penetration test — attempt direct Sphere-to-Cube access, malformed NearMissPacket injection, OAuth2 token replay | Security | All attack vectors blocked; Cube Lockdown Protocol fires correctly on direct access attempt |
| `S6-06` | Documentation: runbooks for Cube lockdown recovery, n8n workflow failure recovery, OAuth2 token refresh failure | Tech Writer | Runbooks reviewed and merged to internal wiki |

**Phase 3 Exit Criteria (MVC Definition of Done):** A user interaction in the Antigravity UI is routed through the multi-agent AI layer, processed by an n8n Plane workflow, evaluated by the Cube when a risk signal is present, and the correct verdict is surfaced in the UI — with the full chain auditable in the Audit Ledger.

---

## MILESTONE SUMMARY TABLE

| Milestone | Target Week | Key Output |
|---|---|---|
| **M1: Cube Online** | Week 4 | Risk Tiering Engine live, Audit Ledger operational, Lockdown Protocol tested |
| **M2: Planes Connected** | Week 8 | n8n mesh live, Google Sheets bridge operational, Cube integrated via NearMissPacket |
| **M3: Sphere Inflated** | Week 12 | Multi-agent AI live, Antigravity frontend deployed, full MVC acceptance passed |

---
---

# DELIVERABLE 3: PROTOTYPE ARCHITECTURE & TECH STACK BLUEPRINT

---

## FULL TECH STACK

### Layer Mapping

```
┌─────────────────────────────────────────────────────────────────────┐
│                     THE OUTER SPHERE (Liquid)                       │
│  Next.js 15 (App Router) · React 19 · Framer Motion · TailwindCSS  │
│  Claude Sonnet 4.6 (Orchestrator) · Haiku 4.5 (Classifiers)        │
│  WebSocket (Sphere Health Monitor) · Vercel Edge Runtime            │
├─────────────────────────────────────────────────────────────────────┤
│                    THE 2D DAMPING PLANES                            │
│  n8n (self-hosted, Docker) · Redis (Shock Absorption Queue)         │
│  PostgreSQL (Plane state store) · Google Sheets API v4 (OAuth2)     │
│  Node.js webhook handlers · OpenAPI 3.1 contract layer              │
├─────────────────────────────────────────────────────────────────────┤
│                     THE INNER CUBE (Solid)                          │
│  Node.js (Fastify) · PostgreSQL with WORM policy (Audit Ledger)     │
│  Git (signed, dual-approval rule store) · YAML rule engine          │
│  Redis (lockdown broadcast channel)                                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Stack Component Detail

| Component | Technology | Rationale |
|---|---|---|
| **Sphere UI Framework** | Next.js 15 (App Router) | Server components reduce AI routing latency; edge runtime co-locates with agent layer |
| **Antigravity Layout Engine** | React 19 + Framer Motion | Spring physics API maps directly to fluid-state metaphor; layout animations are declarative |
| **AI Orchestrator** | Claude Sonnet 4.6 (Anthropic SDK) | Highest reasoning capability for intent classification; structured output for SegmentationPayload construction |
| **AI Classifiers** | Claude Haiku 4.5 | Sub-100ms latency for high-volume, narrow classification tasks (fraud signal tagging, entity type detection) |
| **Automation Engine** | n8n (self-hosted) | Visual workflow graph enables Plane restructuring without code deployments; webhook-native architecture |
| **Shock Absorption Queue** | Redis Streams | Durable, ordered, consumer-group aware — prevents Sphere back-pressure from Plane latency |
| **External Data Bridge** | Google Sheets API v4 + OAuth2 (Web App) | Sheets as accessible data layer for non-technical operators; Web App OAuth2 mandatory for server-side redirect |
| **Cube API Runtime** | Fastify (Node.js) | Lowest overhead HTTP framework; schema validation at framework level before rule engine evaluation |
| **Audit Ledger** | PostgreSQL with trigger-enforced WORM | Row-level triggers reject UPDATE and DELETE operations; immutability enforced at database, not application, layer |
| **Rule Store** | Git (YAML + signed commits) | Version control, dual-approval merge gates, instant rollback — rule changes are code changes |
| **Lockdown Broadcast** | Redis Pub/Sub | Sub-millisecond broadcast to all Plane subscribers; lockdown signal propagates before any in-flight Plane operation can complete |
| **Monitoring** | Prometheus + Grafana | Layer-specific dashboards: Sphere routing latency, Plane queue depth, Cube verdict distribution |
| **Deployment** | Docker Compose (staging), Kubernetes (production path) | Compose for sprint velocity; K8s manifests prepared for production promotion |

---

## THE "CHEMICAL REACTION" INTERFACES — LAYER BOUNDARY APIS

### The Core Problem: How Do the 2D Planes Report a Near Miss Without Blocking the Sphere?

This is the critical architectural challenge. The Sphere must remain fluid and responsive — it cannot wait for Cube evaluation, which may take up to 120ms. The solution is a **decoupled, asynchronous event chain** with a synchronous fallback acknowledgment pattern.

```
SEQUENCE: User Action → Near Miss Detection → Cube Evaluation

[SPHERE]                  [PLANE MESH]                 [INNER CUBE]
   │                           │                              │
   │── POST /api/gateway/v1 ──>│                              │
   │   {SegmentationPayload}   │                              │
   │                           │── Enqueue to Redis ─────>   │
   │<── 202 Accepted ──────────│   {job_id: "abc123"}        │
   │   {job_id: "abc123"}      │                              │
   │                           │── [ASYNC] Plane processes ──│
   │                           │   event, detects risk signal │
   │                           │                              │
   │                           │── POST /api/v1/cube/evaluate>│
   │                           │   {NearMissPacket}           │
   │                           │                              │
   │                           │<── {verdict: "NEAR_MISS"} ──│
   │                           │   [Cube writes Audit Ledger] │
   │                           │                              │
   │                           │── POST /api/sphere/notify ──>│ (Sphere WebSocket)
   │<── WebSocket push ────────│   {job_id, verdict, context} │
   │   {verdict surfaced in UI}│                              │
```

**Key Properties of this Interface:**

1. **The Sphere never waits for Cube evaluation.** It receives a `202 Accepted` with a `job_id` immediately. The UI is unblocked.

2. **The Near Miss Emitter is fire-and-forget with exponential backoff.** If the Cube is temporarily unavailable, the Plane retries (100ms, 200ms, 400ms, 800ms, cap 5s). The Sphere's UI state is not affected during this retry window.

3. **Verdict delivery to the Sphere is via WebSocket push.** The Sphere subscribes to a per-session verdict channel. When the Cube's verdict arrives at the Plane and the Plane dispatches the notify call, the Sphere's WebSocket handler surfaces the Antigravity UI component with the appropriate semantic weight class.

4. **The Cube never initiates communication.** It only responds to `POST /api/v1/cube/evaluate`. The entire system is push-from-Sphere, pull-to-Cube, notify-back-to-Sphere.

---

### NearMissPacket Schema (OpenAPI 3.1 Fragment)

```yaml
NearMissPacket:
  type: object
  required:
    - packet_id
    - originating_workflow
    - entity_id
    - event_timestamp
    - risk_signals
    - segmentation_context
  properties:
    packet_id:
      type: string
      format: uuid
      description: Idempotency key. Cube rejects duplicate packet_ids.
    originating_workflow:
      type: string
      description: n8n workflow ID that generated this packet.
    entity_id:
      type: string
      description: Hashed entity identifier. PII-free at this boundary.
    event_timestamp:
      type: string
      format: date-time
    risk_signals:
      type: array
      items:
        type: object
        properties:
          signal_type:
            type: string
            enum:
              - VELOCITY_BREACH
              - AUTH_ANOMALY
              - BEHAVIORAL_DEVIATION
              - REGULATORY_MATCH
              - BOUNDARY_PROBE
              - RULE_GAP_EXPOSURE
              - DIRECT_ACCESS_ATTEMPT
          signal_value:
            type: number
          threshold_reference:
            type: string
            description: YAML rule ID from the Cube rule store.
    segmentation_context:
      $ref: '#/components/schemas/SegmentationPayload'
```

---

### Cube Verdict Response Schema

```yaml
CubeVerdictResponse:
  type: object
  required:
    - packet_id
    - verdict
    - rule_version_applied
    - audit_ledger_entry_id
    - evaluation_timestamp
  properties:
    packet_id:
      type: string
      format: uuid
    verdict:
      type: string
      enum:
        - WATCHLIST
        - SUSPEND
        - NEAR_MISS
      description: >
        EXACTLY one of three values. No other verdict values are valid.
        WATCHLIST = monitor. SUSPEND = terminate access. NEAR_MISS = log and review.
    rule_version_applied:
      type: string
      description: Git commit SHA of the rule YAML version used for this evaluation.
    audit_ledger_entry_id:
      type: string
      format: uuid
      description: Reference to the immutable Audit Ledger row created for this evaluation.
    evaluation_timestamp:
      type: string
      format: date-time
    remediation_required:
      type: boolean
      description: If true, entity must complete re-verification workflow before access restores.
```

---

### Layer Boundary Security Contracts

| Boundary | Enforcement Mechanism | Violation Consequence |
|---|---|---|
| **Sphere → Plane** | API Gateway Bearer token + IP allowlist | Request dropped; event logged to monitoring |
| **Plane → Cube** | mTLS + service account JWT (Plane services only) | Request dropped; `DIRECT_ACCESS_ATTEMPT` Near Miss signal generated |
| **Sphere → Cube (direct)** | Gateway hard-block; no route exists | `CUBE_LOCKDOWN` broadcast; all Planes halt; Sphere enters maintenance state |
| **Cube → anywhere** | No outbound routes configured at network level | Architectural invariant — Cube has no egress rules |

---

### Antigravity Component Semantic Weight Resolution

```typescript
// Semantic weight determines visual gravity in the Bento Grid
const SEMANTIC_WEIGHT_MAP = {
  CUBE_ORIGINATED_HIGH:   { zIndex: 9999, scale: 1.0,  opacity: 1.0  }, // SUSPEND verdict
  CUBE_ORIGINATED_MEDIUM: { zIndex: 800,  scale: 0.98, opacity: 1.0  }, // WATCHLIST verdict
  CUBE_ORIGINATED_LOW:    { zIndex: 400,  scale: 0.95, opacity: 0.95 }, // NEAR_MISS verdict
  PLANE_ORIGINATED:       { zIndex: 200,  scale: 0.92, opacity: 0.90 },
  SPHERE_NATIVE:          { zIndex: 100,  scale: 0.88, opacity: 0.85 },
} as const;

// Components do not hardcode position — they declare semantic class
// The Antigravity layout engine computes visual prominence at render time
```

---

## ARCHITECTURAL INVARIANTS — THE NON-NEGOTIABLE LAWS

These invariants, once established in Sprint 1, cannot be overridden by any subsequent sprint without a full architecture review:

1. **The Cube has no outbound network routes.** It only responds. It never initiates.
2. **The Sphere has no direct route to the Cube.** Every message must pass through at least one n8n Plane workflow.
3. **The Audit Ledger is append-only at the database layer.** Application-layer immutability is insufficient.
4. **The Risk Tiering Engine produces exactly three verdict values.** No extensions, no aliases, no null verdicts.
5. **The Google Sheets OAuth2 credential is always of type Web Application.** Desktop Application type is prohibited in any environment that runs on a server with a non-localhost redirect URI.
6. **Near Miss events never block the Sphere's response path.** All Near Miss processing is asynchronous from the user's perspective.
7. **Cube lockdown is triggered by any detected attempt to bypass the Plane layer.** The lockdown cannot be configured as a warning — it is always a hard stop.

---

*Project Tesseract V1 Architecture Package — Complete. All three deliverables generated sequentially per specification. The Fractal-State Engine is ready for Sprint 1 kickoff.*
