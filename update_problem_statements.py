import json
from pathlib import Path
from postgres_client import get_connection

BASE_DIR = Path(__file__).resolve().parent
DRAFT_FILE = BASE_DIR / "output" / "problem_statement_drafts.json"


def main():
    drafts = json.loads(DRAFT_FILE.read_text(encoding="utf-8"))

    statements = {}
    for item in drafts:
        problem_id = item.get("problem_id")
        statement = item.get("problem_statement")

        if not problem_id or not isinstance(statement, str) or not statement.strip():
            raise ValueError("Invalid or empty draft found. No database changes made.")

        if problem_id in statements:
            raise ValueError(f"Duplicate problem ID: {problem_id}")

        statements[problem_id] = statement.strip()

    if len(statements) != 200:
        raise ValueError(f"Expected 200 drafts; found {len(statements)}.")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT problem_id, COUNT(*)
                FROM test_cases.generated_test_cases
                WHERE problem_statement IS NULL
                GROUP BY problem_id
            """)
            missing_rows = dict(cur.fetchall())

            draft_ids = set(statements)
            database_ids = set(missing_rows)

            if draft_ids != database_ids:
                raise ValueError(
                    f"Problem IDs do not match. Draft-only: {len(draft_ids - database_ids)}, "
                    f"database-only: {len(database_ids - draft_ids)}. No changes made."
                )

            expected_rows = sum(missing_rows.values())
            print("Draft problem IDs:", len(statements))
            print("Database rows with missing statements:", expected_rows)
            print("All problem IDs match.")
            print("Only NULL problem_statement values will be filled.")
            print("No changes have been made yet.")

            if input("\nType YES to continue: ").strip() != "YES":
                print("Cancelled. Database unchanged.")
                conn.rollback()
                return

            updated_rows = 0
            for problem_id, statement in statements.items():
                cur.execute("""
                    UPDATE test_cases.generated_test_cases
                    SET problem_statement = %s
                    WHERE problem_id = %s
                      AND problem_statement IS NULL
                """, (statement, problem_id))
                updated_rows += cur.rowcount

            if updated_rows != expected_rows:
                raise RuntimeError(
                    f"Expected to update {expected_rows} rows, "
                    f"but updated {updated_rows}. Rolling back."
                )

            cur.execute("""
                SELECT COUNT(*)
                FROM test_cases.generated_test_cases
                WHERE problem_statement IS NULL
            """)
            remaining_null = cur.fetchone()[0]

            if remaining_null != 0:
                raise RuntimeError(
                    f"{remaining_null} rows still have NULL statements. Rolling back."
                )

        conn.commit()
        print(f"Success: updated {updated_rows} rows.")
        print("Only problem_statement was changed.")

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
