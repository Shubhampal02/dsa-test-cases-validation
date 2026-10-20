

import json
import copy
import os



INPUT_FILE = "output/all_200_generated_test_cases.json"
OUTPUT_FILE = "output/expected_outputs_preview.json"


# 1. Search in Rotated Sorted Array
def search_rotated_array(nums, target):
    left = 0
    right = len(nums) - 1

    while left <= right:
        mid = (left + right) // 2

        if nums[mid] == target:
            return mid

        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1

    return -1


# 2. Game of Life
def game_of_life(board):
    if not board:
        return []

    rows = len(board)
    cols = len(board[0])
    result = copy.deepcopy(board)

    for r in range(rows):
        for c in range(cols):
            live = 0

            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue

                    nr = r + dr
                    nc = c + dc

                    if (
                        0 <= nr < rows
                        and 0 <= nc < cols
                        and board[nr][nc] == 1
                    ):
                        live += 1

            if board[r][c] == 1:
                result[r][c] = 1 if live in (2, 3) else 0
            else:
                result[r][c] = 1 if live == 3 else 0

    return result


# 3. Flatten Binary Tree to Linked List
def flatten_tree(tree):
    if tree is None:
        return None

    if not isinstance(tree, dict):
        return tree

    values = []

    def preorder(node):
        if node is None:
            return

        if not isinstance(node, dict):
            values.append(node)
            return

        values.append(node.get("val"))
        preorder(node.get("left"))
        preorder(node.get("right"))

    preorder(tree)

    if not values:
        return None

    result = {"val": values[0], "left": None}
    current = result

    for value in values[1:]:
        current["right"] = {"val": value, "left": None}
        current = current["right"]

    current["right"] = None
    return result


# 4. Basic Calculator
def basic_calculator(expression):
    expression = expression.replace(" ", "")
    index = 0

    def parse():
        nonlocal index
        total = 0
        sign = 1

        while index < len(expression):
            char = expression[index]

            if char.isdigit():
                number = 0

                while (
                    index < len(expression)
                    and expression[index].isdigit()
                ):
                    number = number * 10 + int(expression[index])
                    index += 1

                total += sign * number
                continue

            if char == "+":
                sign = 1
            elif char == "-":
                sign = -1
            elif char == "(":
                index += 1
                total += sign * parse()
                sign = 1
                continue
            elif char == ")":
                index += 1
                return total

            index += 1

        return total

    return parse()


# 5. Two Sum
def two_sum(nums, target):
    seen = {}

    for i, num in enumerate(nums):
        needed = target - num

        if needed in seen:
            return [seen[needed], i]

        seen[num] = i

    return []


# 6. Valid Parentheses
def valid_parentheses(s):
    stack = []
    pairs = {
        ")": "(",
        "]": "[",
        "}": "{"
    }

    for char in s:
        if char in "([{":
            stack.append(char)

        elif char in pairs:
            if not stack or stack.pop() != pairs[char]:
                return False

    return len(stack) == 0


# 7. Maximum Subarray
def maximum_subarray(nums):
    if not nums:
        return 0

    current = nums[0]
    best = nums[0]

    for num in nums[1:]:
        current = max(num, current + num)
        best = max(best, current)

    return best


# 8. Move Zeroes
def move_zeroes(nums):
    result = [num for num in nums if num != 0]
    result.extend([0] * (len(nums) - len(result)))
    return result


# 9. Reverse Integer
def reverse_integer(x):
    sign = -1 if x < 0 else 1
    result = sign * int(str(abs(x))[::-1])

    if result < -(2**31) or result > 2**31 - 1:
        return 0

    return result


# 10. Climbing Stairs
def climbing_stairs(n):
    if n <= 2:
        return n

    first = 1
    second = 2

    for _ in range(3, n + 1):
        first, second = second, first + second

    return second


# 11. Add Two Integers
def add_two_integers(num1, num2):
    return num1 + num2


# 12. Concatenation of Array
def concatenation_of_array(nums):
    return nums + nums


# 13. Longest Common Prefix
def longest_common_prefix(strs):
    if not strs:
        return ""

    prefix = strs[0]

    for word in strs[1:]:
        while not word.startswith(prefix):
            prefix = prefix[:-1]

            if not prefix:
                return ""

    return prefix


# 14. Find Minimum in Rotated Sorted Array
def find_min_rotated(nums):
    if not nums:
        return None

    left = 0
    right = len(nums) - 1

    while left < right:
        mid = (left + right) // 2

        if nums[mid] > nums[right]:
            left = mid + 1
        elif nums[mid] < nums[right]:
            right = mid
        else:
            right -= 1

    return nums[left]

def degree_of_array(nums):
    count = {}
    first_index = {}
    last_index = {}

    for i, num in enumerate(nums):
        count[num] = count.get(num, 0) + 1

        if num not in first_index:
            first_index[num] = i

        last_index[num] = i

    degree = max(count.values())
    answer = len(nums)

    for num in count:
        if count[num] == degree:
            length = last_index[num] - first_index[num] + 1
            answer = min(answer, length)

    return answer


def dot_product(nums1, nums2):
    result = 0

    for a, b in zip(nums1, nums2):
        result += a * b

    return result


def widest_vertical_area(points):
    x_values = sorted(point[0] for point in points)
    answer = 0

    for i in range(1, len(x_values)):
        gap = x_values[i] - x_values[i - 1]
        answer = max(answer, gap)

    return answer


def count_common_words(words1, words2):
    count1 = {}
    count2 = {}

    for word in words1:
        count1[word] = count1.get(word, 0) + 1

    for word in words2:
        count2[word] = count2.get(word, 0) + 1

    answer = 0

    for word in count1:
        if count1[word] == 1 and count2.get(word, 0) == 1:
            answer += 1

    return answer


def min_remove_to_make_valid(s):
    result = []
    open_count = 0

    for char in s:
        if char == "(":
            open_count += 1
            result.append(char)

        elif char == ")":
            if open_count > 0:
                open_count -= 1
                result.append(char)

        else:
            result.append(char)

    final_result = []
    open_to_remove = open_count

    for char in reversed(result):
        if char == "(" and open_to_remove > 0:
            open_to_remove -= 1
        else:
            final_result.append(char)

    return "".join(reversed(final_result))
def main():
    if not os.path.exists(INPUT_FILE):
        print("Input file not found:", INPUT_FILE)
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        original = json.load(file)

    # Work on a copy. Never overwrite the original report.
    preview = copy.deepcopy(original)

    calculated = 0
    unsupported = 0
    unsupported_names = {}
    errors = []

    for case in preview["test_cases"]:


        problem_name = case.get("problem_name", "")
        test_input = case.get("input", {})

        try:
            if problem_name == "Search in Rotated Sorted Array":
                case["output"] = search_rotated_array(
                    test_input["nums"],
                    test_input["target"]
                )

            elif problem_name == "Game of Life":
                case["output"] = game_of_life(test_input["board"])

            elif problem_name == "Flatten Binary Tree to Linked List":
                case["output"] = flatten_tree(
                    test_input.get("tree")
                )

            elif problem_name == "Basic Calculator":
                case["output"] = basic_calculator(
                    test_input["expression"]
                )

            elif problem_name == "Two Sum":
                case["output"] = two_sum(
                    test_input["nums"],
                    test_input["target"]
                )

            elif problem_name == "Valid Parentheses":
                case["output"] = valid_parentheses(
                    test_input["s"]
                )

            elif problem_name == "Maximum Subarray":
                case["output"] = maximum_subarray(
                    test_input["nums"]
                )

            elif problem_name == "Move Zeroes":
                case["output"] = move_zeroes(
                    test_input["nums"]
                )

            elif problem_name == "Reverse Integer":
                case["output"] = reverse_integer(
                    test_input["x"]
                )

            elif problem_name == "Climbing Stairs":
                case["output"] = climbing_stairs(
                    test_input["n"]
                )

            elif problem_name == "Add Two Integers":
                case["output"] = add_two_integers(
                    test_input["num1"],
                    test_input["num2"]
                )

            elif problem_name == "Concatenation of Array":
                case["output"] = concatenation_of_array(
                    test_input["nums"]
                )

            elif problem_name == "Longest Common Prefix":
                case["output"] = longest_common_prefix(
                    test_input["strs"]
                )

            elif problem_name == "Find Minimum in Rotated Sorted Array":
                case["output"] = find_min_rotated(
                    test_input["nums"]
                )

            elif problem_name == "Degree of an Array":
                case["output"] = degree_of_array(test_input["nums"])


            elif problem_name == "Dot Product of Two Sparse Vectors":
                case["output"] = dot_product(
                test_input["nums1"],
                test_input["nums2"]
                )
                calculated += 1

            elif problem_name == "Widest Vertical Area Between Two Points Containing No Points":
                case["output"] = widest_vertical_area(test_input["points"])
                calculated += 1

            elif problem_name == "Count Common Words With One Occurrence":
                case["output"] = count_common_words(
                test_input["words1"],
                test_input["words2"]
                )
                calculated += 1

            elif problem_name == "Minimum Remove to Make Valid Parentheses":
                case["output"] = min_remove_to_make_valid(test_input["s"])
                calculated += 1

            else:
                unsupported += 1
                unsupported_names[problem_name] = (
                    unsupported_names.get(problem_name, 0) + 1
               )
                continue

            calculated += 1

        except (KeyError, TypeError, ValueError, IndexError) as error:
            errors.append({
                "problem_name": problem_name,
                "test_case_id": case.get("test_case_id"),
                "error": str(error)
            })

    preview["calculated_cases"] = calculated
    preview["unsupported_cases"] = unsupported
    preview["error_cases"] = len(errors)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(preview, file, indent=4, ensure_ascii=False)

    print("\nExpected output calculation finished.")
    print("Total test cases:", len(preview["test_cases"]))
    print("Calculated cases:", calculated)
    print("Unsupported cases:", unsupported)
    print("Cases with errors:", len(errors))
    print("Preview saved to:", OUTPUT_FILE)
    print("\nUnsupported problem names:")
    for name, count in sorted(
    unsupported_names.items(),
    key=lambda item: item[1],
    reverse=True
    ):
      print(f"{name}: {count}")

    if errors:
        print("\nFirst 10 errors:")
        for error in errors[:10]:
            print(error)


if __name__ == "__main__":
    main()
