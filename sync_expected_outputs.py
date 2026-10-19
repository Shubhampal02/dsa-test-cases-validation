import sys
import additional_solvers as extra
from collections import Counter

from psycopg2.extras import Json
from postgres_client import get_connection
import calculate_expected_outputs as calc

def generate_parentheses(x):
    n = x["n"]
    result = []

    def backtrack(current, opened, closed):
        if len(current) == 2 * n:
            result.append(current)
            return

        if opened < n:
            backtrack(current + "(", opened + 1, closed)

        if closed < opened:
            backtrack(current + ")", opened, closed + 1)

    backtrack("", 0, 0)
    return result
# Reuse the reference functions already in your project.
SOLVERS = {
        "Merge Sorted Array": lambda inp: (
        sorted(inp["nums1"][:inp["m"]] + inp["nums2"][:inp["n"]])
    ),

    "Linked List Cycle": lambda inp: (
        inp["pos"] != -1 and inp["pos"] < len(inp["vals"])
    ),

    "Time Needed to Buy Tickets": lambda inp: sum(
        max(0, min(t, inp["tickets"][inp["k"]] - (1 if i > inp["k"] else 0)))
        for i, t in enumerate(inp["tickets"])
    ),
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
    "Generate Parentheses": generate_parentheses,

    "Sliding Window Maximum": lambda x: extra.sliding_window_maximum(x["nums"], x["k"]),
}



import additional_solvers as extra

SOLVERS.update({
    "Reaching Points": lambda x: extra.reaching_points(x["sx"], x["sy"], x["tx"], x["ty"]),

    "Subdomain Visit Count": lambda x: extra.subdomain_visit_count(x["cpdomains"]),
"IPO": lambda x: extra.ipo(
    x["k"],
    x.get("w", x.get("initial_capital")),
    x["profits"],
    x["capital"],
),
    "Valid Sudoku":
        lambda x: extra.valid_sudoku(x["board"]),
    "Add Two Numbers":
        lambda x: extra.add_two_numbers(x["l1"], x["l2"]),
    "Evaluate Division":
        lambda x: extra.evaluate_division(
            x["equations"], x["values"], x["queries"]
        ),
    
    "LRU Cache":
        lambda x: extra.lru_cache(
            operations=x.get("operations", x.get("commands")),
            params=x.get("params", x.get("args")),
        ),

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

    "Merge Intervals":
        lambda x: extra.merge_intervals(x["intervals"]),
    "Find the Index of the First Occurrence in a String":
        lambda x: extra.find_first_occurrence(x["haystack"], x["needle"]),
    "Remove Element":
        lambda x: extra.remove_element(x["nums"], x["val"]),
    "Longest Consecutive Sequence":
        lambda x: extra.longest_consecutive_sequence(x["nums"]),
    "Find Words That Can Be Formed by Characters":
        lambda x: extra.count_characters(x["words"], x["chars"]),
    "Ransom Note":
        lambda x: extra.can_construct_ransom_note(
            x["ransomNote"], x["magazine"]
        ),
    "Best Time to Buy and Sell Stock":
        lambda x: extra.max_profit_stock(x["prices"]),

    "Clear Digits":
        lambda x: extra.clear_digits(x["s"]),
    "Largest Palindromic Number":
        lambda x: extra.largest_palindromic_number(x["num"]),
    "Longest Subarray With Maximum Bitwise AND":
        lambda x: extra.longest_subarray_max_bitwise_and(x["nums"]),
    "Longest Unequal Adjacent Groups Subsequence I":
        lambda x: extra.longest_unequal_adjacent_groups(x["words"], x["groups"]),
    "Maximum Number of Balls in a Box":
        lambda x: extra.maximum_balls_in_box(x["lowLimit"], x["highLimit"]),
    "Zigzag Conversion":
        lambda x: extra.zigzag_conversion(x["s"], x["numRows"]),
    "Sqrt(x)":
        lambda x: extra.sqrt_x(x["x"]),
    "Integer to Roman":
        lambda x: extra.integer_to_roman(x["num"]),

    "Generate Parentheses": generate_parentheses,
   
       
})


def main():
    from collections import Counter
    from problem_registry import PROBLEM_NAMES

    apply_changes = "--apply" in sys.argv
    counts = Counter()
    unsupported_names = Counter()
    errors = []
    pending_results = []

    print("Mode:", "WRITE TO AIVEN" if apply_changes else "DRY RUN")
    print("Source of truth: Aiven/PostgreSQL")
    print("JSON file required: No")
    print("Reference implementations:", len(SOLVERS))

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT problem_id, test_case_id, category, pattern, input_data
                FROM test_cases.generated_test_cases
                WHERE output_data IS NULL
                ORDER BY problem_id, test_case_id
            """)
            cases = cursor.fetchall()

            print("Pending cases in Aiven:", len(cases))

            for problem_id, case_id, category, pattern, test_input in cases:
                name = PROBLEM_NAMES.get(problem_id, "")
                solver = SOLVERS.get(name)

                if solver is None:
                    counts["unsupported"] += 1
                    unsupported_names[name or problem_id] += 1
                    continue

                try:
                    result = solver(test_input or {})

                    # Do not save None as an expected output.
                    if result is None:
                        counts["no_result"] += 1
                        if len(errors) < 20:
                            errors.append({
                                "problem": name,
                                "test_case_id": case_id,
                                "error": "Solver returned None; output not saved."
                            })
                        continue

                    pending_results.append(
                        (problem_id, case_id, result, name)
                    )
                    counts["calculated"] += 1

                except Exception as exc:
                    counts["errors"] += 1
                    if len(errors) < 20:
                        errors.append({
                            "problem": name or problem_id,
                            "test_case_id": case_id,
                            "error": str(exc)
                        })

            for problem_id, case_id, result, name in pending_results:
                cursor.execute("""
                    SELECT 1
                    FROM test_cases.generated_test_cases
                    WHERE problem_id = %s
                      AND test_case_id = %s
                      AND (
                          output_data IS NULL
                      )
                    FOR UPDATE
                """, (problem_id, case_id))

                if cursor.fetchone() is None:
                    counts["changed_or_missing"] += 1
                    continue

                counts["matched_pending"] += 1

                if apply_changes:
                    # Change only output_data; preserve review statuses.
                    cursor.execute("""
                        UPDATE test_cases.generated_test_cases
                        SET output_data = %s
                        WHERE problem_id = %s
                          AND test_case_id = %s
                          AND (
                              output_data IS NULL
                          )
                    """, (Json(result), problem_id, case_id))

                    if cursor.rowcount == 1:
                        counts["saved"] += 1
                    else:
                        counts["changed_or_missing"] += 1

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
    for key in (
        "calculated", "matched_pending", "saved", "unsupported",
        "errors", "no_result", "changed_or_missing"
    ):
        print(f"{key.replace('_', ' ').title()}:", counts[key])

    if unsupported_names:
        print("\nUnsupported problem names/IDs:")
        for name, count in unsupported_names.most_common():
            print(f"  {name}: {count}")

    if errors:
        print("\nErrors (first 20):")
        for error in errors:
            print(" ", error)

    if not apply_changes:
        print("\nDRY RUN ONLY: nothing was saved.")


if __name__ == "__main__":
    main()
