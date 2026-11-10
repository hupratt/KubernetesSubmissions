import os

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://todos:todos@localhost:5432/todos"
)

# open=False: the pool is opened/closed in main.py's lifespan
pool = ConnectionPool(
    DATABASE_URL,
    min_size=1,
    max_size=10,
    open=False,
    kwargs={"row_factory": dict_row},
)

SEED = [
    "Learn how Kubernetes Deployments work",
    "Write a Dockerfile for the todo app",
]


def init_schema() -> None:
    """Create the todos table if missing and seed it when empty."""
    with pool.connection() as conn:
        # Serialize concurrent startups (multiple replicas) for this transaction
        conn.execute("SELECT pg_advisory_xact_lock(727274)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                text       VARCHAR(140) NOT NULL
                           CHECK (char_length(text) BETWEEN 1 AND 140),
                done       BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        conn.execute(
            """
            ALTER TABLE todos ADD COLUMN IF NOT EXISTS done BOOLEAN NOT NULL DEFAULT FALSE;
            """
        )
        if conn.execute("SELECT 1 FROM todos LIMIT 1").fetchone() is None:
            with conn.cursor() as cur:
                cur.executemany("INSERT INTO todos (text) VALUES (%s)", [(t,) for t in SEED])
        row = conn.execute(
            "SELECT current_database() AS db, inet_server_addr() AS addr, "
            "inet_server_port() AS port"
        ).fetchone()
        logger.info("Schema ready on %s", row)