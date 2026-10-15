import random
class ArrayGenerator:

    def generate(self, pattern, size, min_value, max_value):

        if pattern == "general_case_with_profit":
            return [7, 1, 5, 3, 6, 4]

        elif pattern == "single_element_array":
            return [min_value]

        elif pattern == "all_elements_are_same":
            value = 50000
            return [value] * size

        elif pattern == "strictly_increasing_prices":
            return list(range(1, size + 1))

        elif pattern == "strictly_decreasing_prices":
            return list(range(size, 0, -1))

        elif pattern == "prices_include_minimum_value_0":
            return [0] + [
                random.randint(min_value, max_value)
                for _ in range(size - 1)
            ]

        elif pattern == "prices_include_maximum_value_100000":
            return [max_value] + [
                random.randint(min_value, max_value)
                for _ in range(size - 1)
            ]

        elif pattern == "buy_at_min_price_0_sell_at_max_price_100000":
            if size < 2:
                return [0]

            return [0] + [
                random.randint(min_value, max_value)
                for _ in range(size - 2)
            ] + [100000]

        elif pattern == "maximum_length_array_with_profit":
            return list(range(0, 100000))

        elif pattern == "maximum_length_array_no_profit":
            return list(range(100000, 0, -1))

        else:
            raise ValueError(f"Unknown pattern: {pattern}")