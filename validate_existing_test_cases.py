
import time

import psycopg2

from postgres_client import get_connection
from services.llm_validator import validate_test_case


def update_validation_result(
    record_id,
    status,
    reason,
    max_retries=3,
):
    """Save a validation result using a fresh database connection."""

    for attempt in range(1, max_retries + 1):
        conn = None

        try:
            conn = get_connection()

            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE test_cases.generated_test_cases
                    SET is_valid = %s,
                        validation_reason = %s
                    WHERE id = %s;
                    """,
                    (status, str(reason)[:4000], record_id),
                )

            conn.commit()
            return True

        except psycopg2.Error as error:
            print(
                f"Database update failed for record {record_id} "
                f"(attempt {attempt}/{max_retries}): {error}"
            )

            if attempt < max_retries:
                time.sleep(attempt * 2)

        finally:
            if conn is not None:
                try:
                    conn.close()
                except psycopg2.Error:
                    pass

    return False


def validate_all_test_cases():
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    problem_id,
                    test_case_id,
                    problem_statement,
                    input_data,
                    output_data
                FROM test_cases.generated_test_cases
                WHERE is_valid IS NULL
                   OR is_valid NOT IN ('Valid', 'Invalid')
                ORDER BY id;
                """
            )

            rows = cursor.fetchall()

    finally:
        conn.close()

    total = len(rows)

    counts = {
        "Valid": 0,
        "Invalid": 0,
        "Needs Review": 0,
    }

    failed_saves = 0

    print(f"Cases requiring validation: {total}")

    for index, row in enumerate(rows, start=1):
        (
            record_id,
            problem_id,
            test_case_id,
            problem_statement,
            input_data,
            stored_output,
        ) = row

        print(
            f"\n[{index}/{total}] "
            f"{problem_id} | {test_case_id}"
        )

        try:
            test_case = {
                "input_data": input_data,
                "stored_expected_output": stored_output,
            }

            result = validate_test_case(
                problem_statement,
                test_case,
            )

            status = result.get("status", "Needs Review")
            reason = result.get(
                "reason",
                "No validation reason provided.",
            )

            if status not in counts:
                status = "Needs Review"
                reason = "Unrecognized validation status."

        except Exception as error:
            status = "Needs Review"
            reason = f"Validation failed: {str(error)[:800]}"

        saved = update_validation_result(
            record_id,
            status,
            reason,
        )

        if not saved:
            failed_saves += 1
            print(
                f"Could not save record {record_id}. "
                "Stopping to avoid losing track of progress."
            )
            break

        counts[status] += 1

        print(f"Status: {status}")
        print(f"Reason: {reason}")

    processed = sum(counts.values())

    print("\n========== VALIDATION SUMMARY ==========")
    print(f"Cases selected: {total}")
    print(f"Successfully saved: {processed}")
    print(f"Valid: {counts['Valid']}")
    print(f"Invalid: {counts['Invalid']}")
    print(f"Needs Review: {counts['Needs Review']}")
    print(f"Failed saves: {failed_saves}")


if __name__ == "__main__":
    validate_all_test_cases()
