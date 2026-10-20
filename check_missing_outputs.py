import json
from pathlib import Path
from postgres_client import get_connection

data = json.loads(
    Path("output/all_200_generated_test_cases.json").read_text(
        encoding="utf-8"
    )
)
cases = data["test_cases"] if isinstance(data, dict) else data
missing = {
    (c["problem_id"], c["test_case_id"])
    for c in cases if c.get("output") is None
}

conn = get_connection()
try:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT problem_id, test_case_id,
                   output_data IS NULL,
                   output_data = 'null'::jsonb,
                   output_data IS NOT NULL
                     AND output_data <> 'null'::jsonb
            FROM test_cases.generated_test_cases
        """)
        rows = cur.fetchall()

    matched = [r for r in rows if (r[0], r[1]) in missing]
    print("JSON cases missing output:", len(missing))
    print("Matching Aiven rows:", len(matched))
    print("Matching rows with SQL NULL:", sum(r[2] for r in matched))
    print("Matching rows with JSON null:", sum(r[3] for r in matched))
    print("Matching rows with non-null output:", sum(r[4] for r in matched))
    print("JSON cases absent from Aiven:", len(missing) - len(matched))
finally:
    conn.close()
