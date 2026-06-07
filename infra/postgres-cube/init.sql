-- ============================================================
-- PROJECT TESSERACT — Inner Cube: PostgreSQL Initialization
-- WORM (Write Once Read Many) enforcement for Audit Ledger
-- ============================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ------------------------------------------------------------
-- Create restricted application role
-- cube_api role: INSERT + SELECT only — no UPDATE, no DELETE
-- ------------------------------------------------------------
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'cube_api') THEN
        CREATE ROLE cube_api WITH LOGIN PASSWORD 'cube_api_changeme_in_production';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE tesseract_cube TO cube_api;
GRANT USAGE ON SCHEMA public TO cube_api;

-- ------------------------------------------------------------
-- Audit Ledger Table (append-only)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_ledger (
    id                   UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    packet_id            UUID        NOT NULL UNIQUE,        -- idempotency key from NearMissPacket
    entity_id_hashed     VARCHAR(64) NOT NULL,               -- SHA-256 of entity identifier — never raw PII
    verdict              VARCHAR(10) NOT NULL
                             CHECK (verdict IN ('WATCHLIST', 'SUSPEND', 'NEAR_MISS')),
    rule_version_applied VARCHAR(40) NOT NULL,               -- Git commit SHA of rule YAML used
    input_hash           CHAR(64)    NOT NULL,               -- SHA-256 of raw NearMissPacket JSON
    evaluation_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    remediation_required BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for reconciliation endpoint queries (read-only path)
CREATE INDEX IF NOT EXISTS idx_audit_ledger_packet_id
    ON audit_ledger (packet_id);

CREATE INDEX IF NOT EXISTS idx_audit_ledger_entity_timestamp
    ON audit_ledger (entity_id_hashed, evaluation_timestamp DESC);

-- ------------------------------------------------------------
-- WORM Enforcement Function
-- Triggered BEFORE any UPDATE or DELETE — raises exception unconditionally
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION prevent_audit_ledger_modification()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION
        'WORM VIOLATION: audit_ledger is append-only. '
        '% operations are prohibited. Attempted on entry id=% packet_id=%',
        TG_OP,
        OLD.id,
        OLD.packet_id;
    RETURN NULL;
END;
$$;

-- BEFORE UPDATE trigger
DROP TRIGGER IF EXISTS trg_audit_ledger_no_update ON audit_ledger;
CREATE TRIGGER trg_audit_ledger_no_update
    BEFORE UPDATE ON audit_ledger
    FOR EACH ROW EXECUTE FUNCTION prevent_audit_ledger_modification();

-- BEFORE DELETE trigger
DROP TRIGGER IF EXISTS trg_audit_ledger_no_delete ON audit_ledger;
CREATE TRIGGER trg_audit_ledger_no_delete
    BEFORE DELETE ON audit_ledger
    FOR EACH ROW EXECUTE FUNCTION prevent_audit_ledger_modification();

-- ------------------------------------------------------------
-- Grant minimum permissions to cube_api (INSERT + SELECT only)
-- Triggers enforce WORM at DB layer; missing grants are second defence
-- ------------------------------------------------------------
GRANT SELECT, INSERT ON audit_ledger TO cube_api;
-- Explicitly: NO UPDATE, NO DELETE grants are issued to cube_api

-- ------------------------------------------------------------
-- Verification: insert a test row, confirm UPDATE fails
-- (This block runs at init time to prove WORM is active)
-- ------------------------------------------------------------
DO $$
DECLARE
    test_id UUID;
BEGIN
    INSERT INTO audit_ledger (
        packet_id, entity_id_hashed, verdict,
        rule_version_applied, input_hash, remediation_required
    ) VALUES (
        '00000000-0000-0000-0000-000000000000',
        'init_verification_row',
        'NEAR_MISS',
        'init',
        'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        FALSE
    ) RETURNING id INTO test_id;

    BEGIN
        UPDATE audit_ledger SET verdict = 'SUSPEND' WHERE id = test_id;
        RAISE EXCEPTION 'WORM TEST FAILED: UPDATE was not blocked — triggers are not active';
    EXCEPTION WHEN others THEN
        IF SQLERRM LIKE '%WORM VIOLATION%' THEN
            RAISE NOTICE 'WORM TEST PASSED: UPDATE correctly blocked on entry %', test_id;
        ELSE
            RAISE;
        END IF;
    END;

    -- Clean up test row (this is the only DELETE ever permitted — at init time via superuser)
    DELETE FROM audit_ledger WHERE id = test_id;
    RAISE NOTICE 'WORM init verification complete. Audit Ledger is operational.';
END;
$$;
