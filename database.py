import os
from urllib.parse import quote_plus

import psycopg2
from dotenv import load_dotenv


NEON_BASE_URL = (
    "postgresql://neondb_owner:{password}"
    "@ep-shiny-paper-adu906me-pooler.c-2.us-east-1.aws.neon.tech"
    "/neondb?sslmode=require&channel_binding=require"
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


__all__ = ["get_neon_connection"]

