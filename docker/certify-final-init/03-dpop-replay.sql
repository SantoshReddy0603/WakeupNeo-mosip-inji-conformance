\connect inji_certify
CREATE TABLE IF NOT EXISTS certify.dpop_replay (
    jkt VARCHAR(100) NOT NULL,
    jti VARCHAR(200) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (jkt, jti)
);
CREATE INDEX IF NOT EXISTS dpop_replay_expiry_idx ON certify.dpop_replay (expires_at);
