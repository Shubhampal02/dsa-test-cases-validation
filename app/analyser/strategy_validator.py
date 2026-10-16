from app.models.strategy import (
    ALLOWED_CATEGORIES,
    TestStrategy,
)


class StrategyValidator:

    @staticmethod
    def validate(strategy: dict) -> list[TestStrategy]:

        if not isinstance(strategy, dict):
            raise ValueError("Strategy must be a dictionary.")

        if "test_strategy" not in strategy:
            raise ValueError("Missing 'test_strategy'.")

        test_strategy = strategy["test_strategy"]

        if not isinstance(test_strategy, list):
            raise ValueError("'test_strategy' must be a list.")

        validated = []

        for index, item in enumerate(test_strategy):

            if not isinstance(item, dict):
                raise ValueError(
                    f"Strategy item {index} must be an object."
                )

            if "category" not in item:
                raise ValueError(
                    f"Strategy item {index} is missing 'category'."
                )

            if "pattern" not in item:
                raise ValueError(
                    f"Strategy item {index} is missing 'pattern'."
                )

            category = item["category"]
            pattern = item["pattern"]

            if category not in ALLOWED_CATEGORIES:
                raise ValueError(
                    f"Invalid category '{category}'. "
                    f"Allowed categories: {ALLOWED_CATEGORIES}"
                )

            if not isinstance(pattern, str) or not pattern.strip():
                raise ValueError(
                    f"Invalid pattern at item {index}."
                )

            validated.append(
                TestStrategy(
                    category=category,
                    pattern=pattern.strip(),
                )
            )

        return validated