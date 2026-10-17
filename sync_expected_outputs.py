import sys
from collections import Counter

from psycopg2.extras import Json
from postgres_client import get_connection
import calculate_expected_outputs as calc


# Reuse the reference functions already in your project.
SOLVERS = {
    "Search in Rotated Sorted Array":
        lambda x: calc.search_rotated_array(x["nums"], x["target"]),
    "Game of Life":
        lambda x: calc.game_of_life(x["board"]),
    "Flatten Binary Tree to Linked List":
        lambda x: calc.flatten_tree(x.get("tree")),
    "Basic Calculator":
        lambda x: calc.basic_calculator(x["expression"]),
    "Two Sum":
        lambda x: calc.two_sum(x["nums"], x["target"]),
    "Valid Parentheses":
        lambda x: calc.valid_parentheses(x["s"]),
    "Maximum Subarray":
        lambda x: calc.maximum_subarray(x["nums"]),
    "Move Zeroes":
        lambda x: calc.move_zeroes(x["nums"]),
    "Reverse Integer":
        lambda x: calc.reverse_integer(x["x"]),
    "Climbing Stairs":
        lambda x: calc.climbing_stairs(x["n"]),
    "Add Two Integers":
        lambda x: calc.add_two_integers(x["num1"], x["num2"]),
    "Concatenation of Array":
        lambda x: calc.concatenation_of_array(x["nums"]),
    "Longest Common Prefix":
        lambda x: calc.longest_common_prefix(x["strs"]),
    "Find Minimum in Rotated Sorted Array":
        lambda x: calc.find_min_rotated(x["nums"]),
    "Degree of an Array":
        lambda x: calc.degree_of_array(x["nums"]),
    "Dot Product of Two Sparse Vectors":
        lambda x: calc.dot_product(x["nums1"], x["nums2"]),
    "Widest Vertical Area Between Two Points Containing No Points":
        lambda x: calc.widest_vertical_area(x["points"]),
    "Count Common Words With One Occurrence":
        lambda x: calc.count_common_words(x["words1"], x["words2"]),
    "Minimum Remove to Make Valid Parentheses":
        lambda x: calc.min_remove_to_make_valid(x["s"]),
}



import additional_solvers as extra

SOLVERS.update({
    "Trapping Rain Water":
        lambda x: extra.trapping_rain_water(x.get("height",x.get("nums"))),
    "First Missing Positive":
        lambda x: extra.first_missing_positive(x["nums"]),
    "Longest Substring Without Repeating Characters":
        lambda x: extra.longest_substring_without_repeating(x["s"]),
    "Roman to Integer":
        lambda x: extra.roman_to_integer(x.get("roman",x.get("s"))),
    "Coin Change":
        lambda x: extra.coin_change(x["coins"], x["amount"]),
    "Valid Palindrome":
        lambda x: extra.valid_palindrome(x["s"]),
    "Palindrome Number":
        lambda x: extra.palindrome_number(x["x"]),
    "Backspace String Compare":
        lambda x: extra.backspace_string_compare(x["S"], x["T"]),
    "Add Strings":
        lambda x: extra.add_strings(x["num1"], x["num2"]),
    "Longest Cycle in a Graph":
        lambda x: extra.longest_cycle(x["edges"]),
})

def main():
    apply_changes = "--apply" in sys.argv

    import json

    input_path = "output/all_200_generated_test_cases.json"

    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    cases = data["test_cases"]
    counts = Counter()
    unsupported_names = Counter()
    errors = []
    pending_results = []

    print("Mode:", "WRITE TO AIVEN" if apply_changes else "DRY RUN")
    print("Cases in JSON:", len(cases))
    print("Reference implementations:", len(SOLVERS))

    # Calculate locally first; no database writes happen in this loop.
    for case in cases:
        name = case.get("problem_name", "")
        solver = SOLVERS.get(name)

        if solver is None:
            counts["unsupported"] += 1
            unsupported_names[name] += 1
            continue

        try:
            result = solver(case.get("input", {}))

            # Do not confuse an unreturned result with a valid JSON null.
            if result is None:
                counts["no_result"] += 1
                errors.append({
                    "problem": name,
                    "test_case_id": case.get("test_case_id"),
                    "error": "Reference function returned None; not saved."
                })
                continue

            pending_results.append((
                case["problem_id"],
                case["test_case_id"],
                result,
                name,
            ))
            counts["calculated"] += 1

        except Exception as exc:
            counts["errors"] += 1
            if len(errors) < 20:
                errors.append({
                    "problem": name,
                    "test_case_id": case.get("test_case_id"),
                    "error": str(exc),
                })

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            for problem_id, case_id, result, name in pending_results:
                cursor.execute("""
                    SELECT output_data
                    FROM test_cases.generated_test_cases
                    WHERE problem_id = %s
                      AND test_case_id = %s
                    LIMIT 1;
                """, (problem_id, case_id))

                row = cursor.fetchone()

                if row is None:
                    counts["not_found_in_db"] += 1
                    continue

                existing_output = row[0]

                # Skip existing outputs; handle SQL NULL and JSON null.
                if existing_output is not None and existing_output != None:
                    # JSON null is returned as Python None by psycopg2,
                    # so use a direct database condition for the decision.
                    pass

                cursor.execute("""
                    SELECT (
                        output_data IS NULL
                        OR output_data = 'null'::jsonb
                    )
                    FROM test_cases.generated_test_cases
                    WHERE problem_id = %s
                      AND test_case_id = %s;
                """, (problem_id, case_id))

                is_pending = cursor.fetchone()[0]

                if not is_pending:
                    counts["already_has_output"] += 1
                    continue

                counts["matched_pending"] += 1

                if apply_changes:
                    cursor.execute("""
                        UPDATE test_cases.generated_test_cases
                        SET output_data = %s,
                            is_valid = %s,
                            validation_reason = %s
                        WHERE problem_id = %s
                          AND test_case_id = %s
                          AND (
                              output_data IS NULL
                              OR output_data = 'null'::jsonb
                          );
                    """, (
                        Json(result),
                        "Needs Review",
                        "Calculated using a local reference implementation; "
                        "independent validation is pending.",
                        problem_id,
                        case_id,
                    ))

                    if cursor.rowcount == 1:
                        counts["saved"] += 1
                    else:
                        counts["skipped_during_update"] += 1

        if apply_changes:
            conn.commit()
        else:
            conn.rollback()

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    print("\n--- SUMMARY ---")
    print("Calculated locally:", counts["calculated"])
    print("Matched pending rows in Aiven:", counts["matched_pending"])
    print("Saved to Aiven:", counts["saved"])
    print("Unsupported cases:", counts["unsupported"])
    print("Calculation errors:", counts["errors"])
    print("No result returned:", counts["no_result"])
    print("IDs not found in Aiven:", counts["not_found_in_db"])
    print("Rows already containing output:", counts["already_has_output"])
    print("Rows skipped during update:", counts["skipped_during_update"])

    if unsupported_names:
        print("\nUnsupported problem names (first 20):")
        for name, count in unsupported_names.most_common(20):
            print(f"{name}: {count}")

    if errors:
        print("\nExamples of errors:")
        for error in errors[:10]:
            print(error)

    if not apply_changes:
        print("\nDRY RUN ONLY: nothing was saved.")
        print("If the results look correct, run:")
        print("python sync_expected_outputs.py --apply")


if __name__ == "__main__":
    main()
