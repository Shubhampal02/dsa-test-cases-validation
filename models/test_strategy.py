class TestStrategy:

    strategies = {
        "Q001": [
            {"category": "sample", "pattern": "general_case_with_profit"},
            {"category": "edge", "pattern": "single_element_array"},
            {"category": "edge", "pattern": "all_elements_are_same"},
            {"category": "boundary", "pattern": "strictly_increasing_prices"},
            {"category": "boundary", "pattern": "strictly_decreasing_prices"},
            {"category": "boundary", "pattern": "prices_include_minimum_value_0"},
            {"category": "boundary", "pattern": "prices_include_maximum_value_100000"},
            {"category": "boundary", "pattern": "buy_at_min_price_0_sell_at_max_price_100000"},
            {"category": "stress", "pattern": "maximum_length_array_with_profit"},
            {"category": "stress", "pattern": "maximum_length_array_no_profit"}
        ]
    }

    @classmethod
    def get_strategy(cls, problem_id):
        return cls.strategies.get(problem_id, [])