"""Create the local SQLite database from the events JSON file.

Usage:
    python scripts/create_db.py
"""

import os
import sys
import sqlite3

import pandas as pd

# Add project root to path so we can import agent.config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent.config import DB_PATH, EVENTS_JSON_PATH, DATA_DIR


def create_local_db(
    json_path: str = EVENTS_JSON_PATH,
    db_path: str = DB_PATH,
    table: str = "local_events",
) -> str:
    """Create a SQLite database from the events JSON file.

    Args:
        json_path: Path to the JSON file containing event objects.
        db_path: Output SQLite database path.
        table: Table name to store events in.

    Returns:
        The path to the created database.
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    # Ensure the data directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    print(f"Loading events from {json_path}...")
    df = pd.read_json(json_path)
    print(f"Loaded {len(df)} records.")

    print(f"Writing to SQLite: {db_path} (table: {table})...")
    conn = sqlite3.connect(db_path)
    df.to_sql(table, conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()
    print("✅ Database created successfully.")
    return db_path


def main():
    try:
        create_local_db()

        # Verify
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM local_events")
        count = cur.fetchone()[0]
        conn.close()
        print(f"Verification: {count} rows in table 'local_events'.")
    except Exception as exc:
        print(f"❌ Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
