import os
from urllib.parse import quote_plus

import psycopg2
from dotenv import load_dotenv


NEON_BASE_URL = (
    "postgresql://neondb_owner:{password}@ep-shiny-paper-adu906me-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)


def get_neon_connection():
    """
    Return a psycopg2 connection to the Neon database.

    The password is read from the DB_PASSWORD variable in the .env file.
    """
    # Load variables from .env (no-op if already loaded)
    load_dotenv()

    db_password = os.getenv("DB_PASSWORD")
    if not db_password:
        raise RuntimeError(
            "DB_PASSWORD is not set. Please add DB_PASSWORD to your .env file."
        )

    # URL-encode the password in case it contains special characters.
    encoded_password = quote_plus(db_password)
    dsn = NEON_BASE_URL.format(password=encoded_password)

    return psycopg2.connect(dsn)


def create_papers_table() -> None:
    """
    Create the simplified `papers` table in the Neon database if it does not exist.
    """
    conn = get_neon_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS papers (
                    id TEXT PRIMARY KEY,
                    doi TEXT,
                    title TEXT NOT NULL,
                    abstract TEXT,
                    publication_date DATE,
                    publication_year INTEGER,
                    created_date TIMESTAMPTZ,
                    updated_date TIMESTAMPTZ,
                    type TEXT,
                    language TEXT,
                    cited_by_count INTEGER,
                    citation_percentile NUMERIC,
                    fwci NUMERIC,
                    is_oa BOOLEAN,
                    oa_status TEXT,
                    oa_url TEXT,
                    primary_topic_id TEXT,
                    primary_topic_name TEXT,
                    primary_domain TEXT,
                    primary_field TEXT,
                    primary_subfield TEXT,
                    ai_concept_score NUMERIC,
                    countries_distinct_count INTEGER,
                    institutions_distinct_count INTEGER,
                    has_fulltext BOOLEAN,
                    is_retracted BOOLEAN,
                    is_paratext BOOLEAN,
                    relevance_score NUMERIC
                );
                """
            )
        conn.commit()
    finally:
        conn.close()


__all__ = ["get_neon_connection", "create_papers_table"]


