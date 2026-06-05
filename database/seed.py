"""
Runs seed SQL files against the database via raw psycopg2 cursor.

Skips 01_* files (schema SQL — handled by Alembic migrations).
Uses DATABASE_URL from environment.
Runs files in alphabetical order so dependencies resolve correctly.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if not DATABASE_URL:
    print("ERROR: DATABASE_URL is not set", file=sys.stderr)
    sys.exit(1)

SEED_DIR = PROJECT_ROOT / "database" / "init"

if not SEED_DIR.is_dir():
    print(f"ERROR: seed directory not found: {SEED_DIR}", file=sys.stderr)
    sys.exit(1)

seed_files = sorted(
    f for f in os.listdir(SEED_DIR)
    if f.endswith(".sql") and not f.startswith("01_")
)

if not seed_files:
    print("No seed files to run.")
    sys.exit(0)

engine = create_engine(DATABASE_URL)

print("Running seed scripts...")

with engine.raw_connection() as raw_conn:
    cursor = raw_conn.cursor()
    try:
        for filename in seed_files:
            filepath = SEED_DIR / filename
            sql = filepath.read_text(encoding="utf-8")
            print(f"  Seeding: {filename}")
            cursor.execute(sql)
        raw_conn.commit()
        print(f"Done. {len(seed_files)} seed files executed successfully.")
    except Exception:
        raw_conn.rollback()
        print(f"ERROR: seed failed on {filename}", file=sys.stderr)
        raise

engine.dispose()
