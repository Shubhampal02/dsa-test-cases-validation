
from app.models.problem import Problem
from app.analyser.strategy_validator import StrategyValidator
from app.analyser.llm_strategy_generator import LLMStrategyGenerator


class ProblemAnalyzer:
    def __init__(self):
        self.llm = LLMStrategyGenerator()

    @staticmethod
    def validate_strategy(strategy: dict) -> list[dict]:
        validated = StrategyValidator.validate(
            {"test_strategy": strategy}
        )

        return [
            {
                "category": item.category,
                "pattern": item.pattern,
            }
            for item in validated
        ]

    def analyze_many(self, problems: list[Problem]) -> list[dict]:
        if not problems:
            return []

        batch_results = self.llm.generate_strategies_batch(problems)
        results_by_id = {
            item["problem_id"]: item for item in batch_results
        }

        analyzed_results = []

        for problem in problems:
            item = results_by_id[problem.id]

            validated_strategy = self.validate_strategy(
                item["test_strategy"]
            )

            analyzed_results.append(
                {
                    "problem_id": problem.id,
                    "problem_name": problem.title,
                    "test_strategy": validated_strategy,
                }
            )

        return analyzed_results
