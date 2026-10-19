from postgres_client import get_connection

invalid_cases = {
    "TC_67eb8ab4_003": (
        "Random Pick with Weight input is incomplete: weights are missing."
    ),
    "TC_ba9a0d92_001": (
        "Invalid input for standard problem constraints: k must be at least 2."
    ),
    "TC_ba9a0d92_002": (
        "Invalid input for standard problem constraints: k must be less than nums length."
    ),
    "TC_ba9a0d92_003": (
        "Invalid input for standard problem constraints: k must be at least 2."
    ),
    "TC_ba9a0d92_004": (
        "Invalid input for standard problem constraints: k must be less than nums length."
    ),
}

conn = get_connection()
try:
    with conn.cursor() as cur:
        for test_case_id, reason in invalid_cases.items():
            cur.execute("""
                UPDATE test_cases.generated_test_cases
                SET is_valid = 'false',
                    validation_reason = %s,
                    review_status = 'needs_correction'
                WHERE test_case_id = %s
                  AND output_data = 'null'::jsonb
                RETURNING test_case_id
            """, (reason, test_case_id))

            updated = cur.fetchone()
            if updated:
                print("Marked invalid:", updated[0])
            else:
                print("Skipped; row missing or output no longer null:", test_case_id)

    conn.commit()
    print("Validation metadata committed.")
except Exception:
    conn.rollback()
    raise
finally:
    conn.close()
