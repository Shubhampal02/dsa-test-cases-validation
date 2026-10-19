import json
from pathlib import Path
from postgres_client import get_connection

BASE_DIR = Path(__file__).resolve().parent
DRAFT_FILE = BASE_DIR / "output" / "problem_statement_drafts.json"

drafts = json.loads(DRAFT_FILE.read_text(encoding="utf-8"))
draft_ids = {
    item["problem_id"]
    for item in drafts
    if item.get("problem_statement")
}

conn = get_connection()

try:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT DISTINCT problem_id
            FROM test_cases.generated_test_cases
            WHERE problem_statement IS NULL
        """)
        db_ids = {row[0] for row in cur.fetchall()}

        cur.execute("""
            SELECT COUNT(*)
            FROM test_cases.generated_test_cases
            WHERE problem_statement IS NULL
        """)
        missing_rows = cur.fetchone()[0]

    print("Draft IDs with statements:", len(draft_ids))
    print("Database IDs missing statements:", len(db_ids))
    print("Database rows missing statements:", missing_rows)
    print("Draft-only IDs:", len(draft_ids - db_ids))
    print("Database-only IDs:", len(db_ids - draft_ids))
    print("ID sets match:", draft_ids == db_ids)

finally:
    conn.close()
