def trapping_rain_water(nums):
    left, right = 0, len(nums) - 1
    left_max = right_max = water = 0

    while left < right:
        if nums[left] <= nums[right]:
            left_max = max(left_max, nums[left])
            water += left_max - nums[left]
            left += 1
        else:
            right_max = max(right_max, nums[right])
            water += right_max - nums[right]
            right -= 1

    return water


def first_missing_positive(nums):
    values = set(nums)
    number = 1
    while number in values:
        number += 1
    return number


def longest_substring_without_repeating(s):
    last_seen = {}
    left = longest = 0

    for right, char in enumerate(s):
        if char in last_seen and last_seen[char] >= left:
            left = last_seen[char] + 1
        last_seen[char] = right
        longest = max(longest, right - left + 1)

    return longest


def roman_to_integer(roman):
    values = {
        "I": 1, "V": 5, "X": 10, "L": 50,
        "C": 100, "D": 500, "M": 1000
    }
    total = 0

    for i, char in enumerate(roman):
        if i + 1 < len(roman) and values[char] < values[roman[i + 1]]:
            total -= values[char]
        else:
            total += values[char]

    return total


def coin_change(coins, amount):
    dp = [float("inf")] * (amount + 1)
    dp[0] = 0

    for value in range(1, amount + 1):
        for coin in coins:
            if coin <= value:
                dp[value] = min(dp[value], dp[value - coin] + 1)

    return -1 if dp[amount] == float("inf") else dp[amount]


def valid_palindrome(s):
    cleaned = "".join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]


def palindrome_number(x):
    return x >= 0 and str(x) == str(x)[::-1]


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


def add_strings(num1, num2):
    i, j = len(num1) - 1, len(num2) - 1
    carry = 0
    result = []

    while i >= 0 or j >= 0 or carry:
        a = int(num1[i]) if i >= 0 else 0
        b = int(num2[j]) if j >= 0 else 0
        total = a + b + carry

        result.append(str(total % 10))
        carry = total // 10
        i -= 1
        j -= 1

    return "".join(reversed(result))


def longest_cycle(edges):
    n = len(edges)
    visited = [False] * n
    longest = -1

    for start in range(n):
        if visited[start]:
            continue

        current = start
        step = 0
        local_steps = {}

        while current != -1 and not visited[current]:
            visited[current] = True
            local_steps[current] = step
            step += 1
            current = edges[current]

        if current != -1 and current in local_steps:
            longest = max(longest, step - local_steps[current])

    return longest
