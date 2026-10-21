from dataclasses import dataclass


ALLOWED_CATEGORIES = {
    "sample",
    "basic",
    "edge",
    "boundary",
    "negative",
    "stress",
}


@dataclass
class TestStrategy:
    category: str
    pattern: str


@dataclass
class StrategyResult:
    test_strategy: list[TestStrategy]