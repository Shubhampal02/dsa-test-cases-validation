import json
from pathlib import Path
from postgres_client import get_connection

source = Path("output/all_200_generated_test_cases.json")
destination = Path("output/all_200_generated_test_cases.recovered.json")

data = json.loads(source.read_text(encoding="utf-8"))
cases = data["test_cases"] if isinstance(data, dict) else data

conn = get_connection()
try:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT problem_id, test_case_id, output_data
            FROM test_cases.generated_test_cases
            WHERE output_data IS NOT NULL
              AND output_data <> 'null'::jsonb
        """)
        outputs = {
            (problem_id, case_id): output
            for problem_id, case_id, output in cur.fetchall()
        }
finally:
    conn.close()

recovered = 0
still_missing = 0

for case in cases:
    key = (case["problem_id"], case["test_case_id"])
    if case.get("output") is None and key in outputs:
        case["output"] = outputs[key]
        recovered += 1

    if case.get("output") is None:
        still_missing += 1

destination.write_text(
    json.dumps(data, indent=2, ensure_ascii=False),
    encoding="utf-8",
)

print("Outputs recovered from Aiven:", recovered)
print("Cases still missing outputs:", still_missing)
print("New file saved to:", destination)
print("Original JSON preserved:", source.exists())
