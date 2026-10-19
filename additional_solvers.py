import heapq

def ipo(k, w, profits, capital):
    projects = sorted(zip(capital, profits))
    available_profits = []
    current_capital = w
    index = 0

    for _ in range(k):
        while (
            index < len(projects)
            and projects[index][0] <= current_capital
        ):
            heapq.heappush(available_profits, -projects[index][1])
            index += 1

        if not available_profits:
            break

        current_capital -= heapq.heappop(available_profits)

    return current_capital

from collections import deque

def sliding_window_maximum(nums, k):
    if not nums or k <= 0 or k > len(nums):
        return []

    result = []
    window = deque()

    for i in range(len(nums)):
        while window and window[0] <= i - k:
            window.popleft()

        while window and nums[window[-1]] <= nums[i]:
            window.pop()

        window.append(i)

        if i >= k - 1:
            result.append(nums[window[0]])

    return result
def backspace_string_compare(s, t):
    def process(text):
        result = []

        for char in text:
            if char == "#":
                if result:
                    result.pop()
            else:
                result.append(char)

        return "".join(result)

    return process(s) == process(t)

def evaluate_division(equations, values, queries):
    from collections import defaultdict, deque

    graph = defaultdict(list)

    for (a, b), value in zip(equations, values):
        if value == 0:
            continue
        graph[a].append((b, value))
        graph[b].append((a, 1.0 / value))

    results = []

    for start, end in queries:
        if start not in graph or end not in graph:
            results.append(-1.0)
            continue

        if start == end:
            results.append(1.0)
            continue

        queue = deque([(start, 1.0)])
        visited = {start}
        answer = -1.0

        while queue:
            node, product = queue.popleft()

            if node == end:
                answer = product
                break

            for neighbor, weight in graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, product * weight))

        results.append(answer)

    return results


def evaluate_division(equations, values, queries):
    from collections import defaultdict, deque

    graph = defaultdict(list)

    for (a, b), value in zip(equations, values):
        graph[a].append((b, value))

        if value != 0:
            graph[b].append((a, 1.0 / value))

    results = []

    for start, end in queries:
        if start not in graph or end not in graph:
            results.append(-1.0)
            continue

        if start == end:
            results.append(1.0)
            continue

        queue = deque([(start, 1.0)])
        visited = {start}
        answer = -1.0

        while queue:
            node, product = queue.popleft()

            if node == end:
                answer = product
                break

            for neighbor, weight in graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, product * weight))

        results.append(answer)

    return results


def subdomain_visit_count(cpdomains):
    from collections import defaultdict

    counts = defaultdict(int)

    for entry in cpdomains:
        parts = entry.split()

        if len(parts) != 2:
            continue

        try:
            visits = int(parts[0])
        except ValueError:
            continue

        if visits < 0:
            continue

        domain = parts[1]
        labels = domain.split(".")

        for i in range(len(labels)):
            subdomain = ".".join(labels[i:])
            counts[subdomain] += visits

    return [f"{count} {domain}" for domain, count in sorted(counts.items())]


def path_with_maximum_gold(grid):
    if not grid or not grid[0]:
        return 0

    rows = len(grid)
    cols = len(grid[0])
    best = 0

    def dfs(r, c, total):
        nonlocal best

        if r < 0 or r >= rows or c < 0 or c >= cols:
            return
        if grid[r][c] == 0:
            return

        gold = grid[r][c]
        grid[r][c] = 0
        total += gold
        best = max(best, total)

        dfs(r + 1, c, total)
        dfs(r - 1, c, total)
        dfs(r, c + 1, total)
        dfs(r, c - 1, total)

        grid[r][c] = gold

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] > 0:
                dfs(r, c, 0)

    return best


def trapping_rain_water(height):
    if not height or len(height) < 3:
        return 0

    left = 0
    right = len(height) - 1
    left_max = 0
    right_max = 0
    water = 0

    while left < right:
        if height[left] <= height[right]:
            left_max = max(left_max, height[left])
            water += left_max - height[left]
            left += 1
        else:
            right_max = max(right_max, height[right])
            water += right_max - height[right]
            right -= 1

    return water


def first_missing_positive(nums):
    nums = nums.copy()
    n = len(nums)

    for i in range(n):
        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
            target = nums[i] - 1
            nums[i], nums[target] = nums[target], nums[i]

    for i in range(n):
        if nums[i] != i + 1:
            return i + 1

    return n + 1

def valid_sudoku(board):
    if len(board) != 9 or any(len(row) != 9 for row in board):
        return False

    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]

    for r in range(9):
        for c in range(9):
            value = board[r][c]

            if value in (".", 0, "0", None):
                continue

            value = str(value)
            if value not in "123456789":
                return False

            box = (r // 3) * 3 + c // 3

            if value in rows[r] or value in cols[c] or value in boxes[box]:
                return False

            rows[r].add(value)
            cols[c].add(value)
            boxes[box].add(value)

    return True


def add_two_numbers(l1, l2):
    result = []
    carry = 0
    i = 0
    j = 0

    while i < len(l1) or j < len(l2) or carry:
        a = l1[i] if i < len(l1) else 0
        b = l2[j] if j < len(l2) else 0

        total = a + b + carry
        result.append(total % 10)
        carry = total // 10

        i += 1
        j += 1

    return result


def lru_cache(operations=None, params=None, commands=None, args=None):
    operations = operations if operations is not None else commands
    params = params if params is not None else args

    if not operations or not params or len(operations) != len(params):
        raise ValueError("LRU Cache requires matching operations and params")

    from collections import OrderedDict

    cache = OrderedDict()
    result = []
    capacity = 0

    for operation, values in zip(operations, params):
        if operation in ("LRUCache", "LRU"):
            capacity = values[0]
            result.append(None)

        elif operation == "put":
            key, value = values
            if key in cache:
                del cache[key]
            cache[key] = value

            if len(cache) > capacity:
                cache.popitem(last=False)

            result.append(None)

        elif operation == "get":
            key = values[0]
            if key not in cache:
                result.append(-1)
            else:
                cache.move_to_end(key)
                result.append(cache[key])

        else:
            raise ValueError(f"Unsupported LRU operation: {operation}")

    return result
    


def roman_to_integer(s):
    values = {
        "I": 1, "V": 5, "X": 10,
        "L": 50, "C": 100, "D": 500, "M": 1000
    }

    total = 0
    for i in range(len(s)):
        if s[i] not in values:
            raise ValueError(f"Invalid Roman numeral character: {s[i]}")

        if i + 1 < len(s) and values[s[i]] < values[s[i + 1]]:
            total -= values[s[i]]
        else:
            total += values[s[i]]

    return total


def valid_palindrome(s):
    cleaned = [ch.lower() for ch in s if ch.isalnum()]
    return cleaned == cleaned[::-1]


def palindrome_number(x):
    if x < 0:
        return False

    original = x
    reversed_number = 0

    while x > 0:
        digit = x % 10
        reversed_number = reversed_number * 10 + digit
        x //= 10

    return original == reversed_number


def longest_substring_without_repeating(s):
    last_seen = {}
    left = 0
    longest = 0

    for right, char in enumerate(s):
        if char in last_seen and last_seen[char] >= left:
            left = last_seen[char] + 1

        last_seen[char] = right
        longest = max(longest, right - left + 1)

    return longest


def add_strings(num1, num2):
    i = len(num1) - 1
    j = len(num2) - 1
    carry = 0
    result = []

    while i >= 0 or j >= 0 or carry:
        digit1 = int(num1[i]) if i >= 0 else 0
        digit2 = int(num2[j]) if j >= 0 else 0

        total = digit1 + digit2 + carry
        result.append(str(total % 10))
        carry = total // 10

        i -= 1
        j -= 1

    return "".join(result[::-1])


def coin_change(coins, amount):
    if amount < 0:
        return -1

    dp = [float("inf")] * (amount + 1)
    dp[0] = 0

    for current in range(1, amount + 1):
        for coin in coins:
            if coin > 0 and coin <= current:
                dp[current] = min(
                    dp[current],
                    dp[current - coin] + 1
                )

    return dp[amount] if dp[amount] != float("inf") else -1


def longest_cycle(edges):
    n = len(edges)
    visited = [False] * n
    longest = -1

    for start in range(n):
        if visited[start]:
            continue

        current = start
        distance = {}
        steps = 0

        while current != -1 and not visited[current]:
            visited[current] = True
            distance[current] = steps
            steps += 1
            current = edges[current]

            if current in distance:
                longest = max(longest, steps - distance[current])
                break

    return longest


def merge_intervals(intervals):
    if not intervals:
        return []

    intervals = sorted(intervals, key=lambda interval: interval[0])
    merged = [intervals[0][:]]

    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])

    return merged


def find_first_occurrence(haystack, needle):
    if needle == "":
        return 0

    for i in range(len(haystack) - len(needle) + 1):
        if haystack[i:i + len(needle)] == needle:
            return i

    return -1


def remove_element(nums, val):
    kept = [num for num in nums if num != val]
    return len(kept)


def longest_consecutive_sequence(nums):
    values = set(nums)
    longest = 0

    for num in values:
        if num - 1 not in values:
            current = num
            length = 1

            while current + 1 in values:
                current += 1
                length += 1

            longest = max(longest, length)

    return longest


def count_characters(words, chars):
    available = {}
    for char in chars:
        available[char] = available.get(char, 0) + 1

    total = 0

    for word in words:
        needed = {}
        for char in word:
            needed[char] = needed.get(char, 0) + 1

        if all(count <= available.get(char, 0)
               for char, count in needed.items()):
            total += len(word)

    return total


def can_construct_ransom_note(ransomNote, magazine):
    available = {}
    for char in magazine:
        available[char] = available.get(char, 0) + 1

    for char in ransomNote:
        if available.get(char, 0) == 0:
            return False
        available[char] -= 1

    return True


def max_profit_stock(prices):
    if not prices:
        return 0

    lowest = prices[0]
    best_profit = 0

    for price in prices[1:]:
        best_profit = max(best_profit, price - lowest)
        lowest = min(lowest, price)

    return best_profit


def clear_digits(s):
    result = []
    for char in s:
        if char.isdigit():
            if result:
                result.pop()
        else:
            result.append(char)
    return "".join(result)


def largest_palindromic_number(num):
    counts = {}
    for digit in num:
        counts[digit] = counts.get(digit, 0) + 1

    left = []
    for digit in "9876543210":
        pairs = counts.get(digit, 0) // 2
        if digit == "0" and not left:
            continue
        left.extend([digit] * pairs)

    middle = ""
    for digit in "9876543210":
        if counts.get(digit, 0) % 2:
            middle = digit
            break

    result = "".join(left) + middle + "".join(left[::-1])
    return result if result else "0"


def longest_subarray_max_bitwise_and(nums):
    if not nums:
        return 0

    maximum = max(nums)
    longest = 0
    current = 0

    for num in nums:
        if num == maximum:
            current += 1
            longest = max(longest, current)
        else:
            current = 0

    return longest


def longest_unequal_adjacent_groups(words, groups):
    result = []
    previous_group = None

    for word, group in zip(words, groups):
        if previous_group is None or group != previous_group:
            result.append(word)
            previous_group = group

    return result


def maximum_balls_in_box(lowLimit, highLimit):
    counts = {}

    for number in range(lowLimit, highLimit + 1):
        digit_sum = sum(int(digit) for digit in str(number))
        counts[digit_sum] = counts.get(digit_sum, 0) + 1

    return max(counts.values(), default=0)


def zigzag_conversion(s, numRows):
    if numRows <= 1 or numRows >= len(s):
        return s

    rows = [""] * numRows
    row = 0
    direction = 1

    for char in s:
        rows[row] += char

        if row == 0:
            direction = 1
        elif row == numRows - 1:
            direction = -1

        row += direction

    return "".join(rows)


def sqrt_x(x):
    if x < 2:
        return x

    left, right = 1, x // 2

    while left <= right:
        mid = (left + right) // 2

        if mid * mid == x:
            return mid
        if mid * mid < x:
            left = mid + 1
        else:
            right = mid - 1

    return right


def integer_to_roman(num):
    values = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")
    ]

    result = []
    for value, symbol in values:
        while num >= value:
            result.append(symbol)
            num -= value

    return "".join(result)

def reaching_points(sx, sy, tx, ty):
    while tx >= sx and ty >= sy:
        if tx == sx and ty == sy:
            return True

        if tx > ty:
            if ty == sy:
                return (tx - sx) % ty == 0
            tx %= ty
        else:
            if tx == sx:
                return (ty - sy) % tx == 0
            ty %= tx

    return False