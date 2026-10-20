import sys
from psycopg2.extras import Json
from postgres_client import get_connection

# Only outputs calculated for valid inputs under the standard
# definitions of these problems.
candidates = {
    ("3007c3d4-cd02-43a4-a35a-f4ceb72fa713", "TC_3007c3d4_004"): 22500,

    ("ba9a0d92-c2a6-4cdd-b826-dcf6ee11e356", "TC_ba9a0d92_005"): 3,
    ("ba9a0d92-c2a6-4cdd-b826-dcf6ee11e356", "TC_ba9a0d92_006"): 6,
    ("ba9a0d92-c2a6-4cdd-b826-dcf6ee11e356", "TC_ba9a0d92_007"): 9,
    ("ba9a0d92-c2a6-4cdd-b826-dcf6ee11e356", "TC_ba9a0d92_008"): 14,
    ("ba9a0d92-c2a6-4cdd-b826-dcf6ee11e356", "TC_ba9a0d92_009"): 2999999995,
    ("ba9a0d92-c2a6-4cdd-b826-dcf6ee11e356", "TC_ba9a0d92_010"): 6,
    ("ba9a0d92-c2a6-4cdd-b826-dcf6ee11e356", "TC_ba9a0d92_011"): 6,
}

apply_changes = "--apply" in sys.argv
conn = get_connection()

try:
    with conn.cursor() as cur:
        ready = []

        for (problem_id, test_case_id), output in candidates.items():
            cur.execute("""
                SELECT output_data
                FROM test_cases.generated_test_cases
                WHERE problem_id = %s AND test_case_id = %s
            """, (problem_id, test_case_id))
            row = cur.fetchone()

            if row is None:
                print("SKIP - row not found:", test_case_id)
            elif row[0] is not None:
                # JSONB null is returned by psycopg2 as Python None too;
                # non-null existing outputs are never overwritten.
                print("SKIP - output already exists:", test_case_id)
            else:
                ready.append((problem_id, test_case_id, output))
                print("READY:", test_case_id, "->", output)

        print("\nRows eligible for update:", len(ready))

        if apply_changes:
            for problem_id, test_case_id, output in ready:
                cur.execute("""
                    UPDATE test_cases.generated_test_cases
                    SET output_data = %s
                    WHERE problem_id = %s
                      AND test_case_id = %s
                      AND output_data = 'null'::jsonb
                    RETURNING test_case_id
                """, (Json(output), problem_id, test_case_id))

                if cur.fetchone() is None:
                    raise RuntimeError(
                        f"Row changed unexpectedly: {test_case_id}"
                    )

            conn.commit()
            print("Committed updates:", len(ready))
        else:
            conn.rollback()
            print("DRY RUN ONLY - Aiven was not changed.")
            print("Review the list before running with --apply.")

except Exception:
    conn.rollback()
    raise
finally:
    conn.close()
