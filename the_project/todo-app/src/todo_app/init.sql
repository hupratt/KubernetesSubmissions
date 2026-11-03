-- Runs once, on the first start of an empty Postgres data directory.
-- Works whether or not POSTGRES_DB is already set to "todos".
SELECT 'CREATE DATABASE todos'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'todos')\gexec

\connect todos

CREATE TABLE IF NOT EXISTS todos (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    text       VARCHAR(140) NOT NULL CHECK (char_length(text) BETWEEN 1 AND 140),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Seed the two todos that were hardcoded before (only if the table is empty)
INSERT INTO todos (text)
SELECT t FROM (VALUES
    ('Learn how Kubernetes Deployments work'),
    ('Write a Dockerfile for the todo app')
) AS v(t)
WHERE NOT EXISTS (SELECT 1 FROM todos);