from pathlib import Path

p = Path("automate_all_outputs.py")
s = p.read_text()

old = "        calculated_results.extend(problem_results)\n"

new = '''        calculated_results.extend(problem_results)

        # Save progress after each problem
        RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        RESULTS_FILE.write_text(
            json.dumps(calculated_results, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # Save newly calculated outputs to PostgreSQL immediately
        if apply_changes and problem_results:
            conn = get_connection()
            try:
                with conn.cursor() as cursor:
                    for result in problem_results:
                        cursor.execute(
                            """
                            UPDATE test_cases.generated_test_cases
                            SET output_data = %s,
                                review_status = 'not_independently_verified'
                            WHERE problem_id = %s
                              AND test_case_id = %s
                              AND (
                                  output_data IS NULL
                                  OR output_data = 'null'::jsonb
                              )
                            """,
                            (
                                Json(result["output"]),
                                result["problem_id"],
                                result["test_case_id"],
                            ),
                        )
                        report["saved_to_database"] += cursor.rowcount
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
'''

if s.count(old) != 1:
    raise SystemExit("Expected insertion point not found exactly once; file unchanged.")

p.write_text(s.replace(old, new, 1))
print("Patch inserted.")
