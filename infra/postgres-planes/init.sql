-- ============================================================
-- PROJECT TESSERACT — 2D Planes: PostgreSQL Initialization
-- State store for Plane workflow tracking and routing metadata
-- NOTE: No WORM policy here — Plane state is mutable by design.
--       Only the Cube's Audit Ledger is WORM-enforced.
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ------------------------------------------------------------
-- Application role for Plane services
-- ------------------------------------------------------------
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'planes_app') THEN
        CREATE ROLE planes_app WITH LOGIN PASSWORD 'planes_app_changeme_in_production';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE tesseract_planes TO planes_app;
GRANT USAGE ON SCHEMA public TO planes_app;

-- ------------------------------------------------------------
-- Job tracking table: maps job_id lifecycle across Plane hops
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS job_tracking (
    id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id       UUID        NOT NULL UNIQUE,
    status       VARCHAR(20) NOT NULL DEFAULT 'QUEUED'
                     CHECK (status IN ('QUEUED','PROCESSING','VERDICT_RECEIVED','TIMEOUT','DLQ')),
    workflow_id  VARCHAR(128),
    entity_id_hashed VARCHAR(64),
    enqueued_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    verdict      VARCHAR(10) CHECK (verdict IN ('WATCHLIST', 'SUSPEND', 'NEAR_MISS')),
    dlq_reason   VARCHAR(64),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_job_tracking_job_id ON job_tracking (job_id);
CREATE INDEX IF NOT EXISTS idx_job_tracking_status ON job_tracking (status);
CREATE INDEX IF NOT EXISTS idx_job_tracking_enqueued ON job_tracking (enqueued_at);

GRANT SELECT, INSERT, UPDATE ON job_tracking TO planes_app;

-- ------------------------------------------------------------
-- Routing ruleset version tracking
-- Mirrors the versioned JSON files in /planes/routing-rules/
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS routing_ruleset_versions (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    version     VARCHAR(20) NOT NULL UNIQUE,
    file_path   VARCHAR(256) NOT NULL,
    activated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    activated_by VARCHAR(64),
    is_active   BOOLEAN NOT NULL DEFAULT FALSE
);

GRANT SELECT, INSERT, UPDATE ON routing_ruleset_versions TO planes_app;
