-- Schema creation (optional). Uses env var SUGGESTIONS_SCHEMA when running via psql or migration tools.
-- If you want a dedicated schema, create it first (safe to run repeatedly):
-- CREATE SCHEMA IF NOT EXISTS cold_suggestions;

-- Table for storing user-submitted suggestions (adjust schema name if needed)
CREATE TABLE IF NOT EXISTS user_suggestions (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    payload JSONB NOT NULL,
    client_ip VARCHAR(64),
    user_agent TEXT,
    source VARCHAR(256),
    token_sub VARCHAR(256)
);

-- Index to speed up querying by created_at and json operations if needed
CREATE INDEX IF NOT EXISTS idx_user_suggestions_created_at ON user_suggestions (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_suggestions_payload_gin ON user_suggestions USING GIN (payload);
