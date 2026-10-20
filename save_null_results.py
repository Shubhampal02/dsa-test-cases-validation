from psycopg2.extras import Json
from postgres_client import get_connection

cases = {
    "TC_9d2b6435_003": (
        "No second distinct salary exists; standard Second Highest Salary "
        "semantics return null. Independent verification is pending."
    ),
    "TC_9d2b6435_004": (
        "All salaries are identical, so no second distinct salary exists; "
        "standard Second Highest Salary semantics return null. "
        "Independent verification is pending."
    ),
    "TC_a070cccc_001": (
        "The existing flatten_tree reference function returns null for an "
        "empty tree. Independent verification is pending."
    ),
}

conn = get_connection()
try:
    with conn.cursor() as cur:
        for case_id, reason in cases.items():
            cur.execute("""
                UPDATE test_cases.generated_test_cases
                SET output_data = %s,
                    is_valid = 'true',
                    validation_reason = %s,
                    review_status = 'Needs Review'
                WHERE test_case_id = %s
                  AND (output_data IS NULL OR output_data = 'null'::jsonb)
                RETURNING test_case_id
            """, (Json(None), reason, case_id))

            row = cur.fetchone()
            print("Saved null candidate:" if row else "Skipped:", case_id)

    conn.commit()
    print("Committed. These results still require independent review.")
except Exception:
    conn.rollback()
    raise
finally:
    conn.close()
