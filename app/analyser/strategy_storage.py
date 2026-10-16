import json
from pathlib import Path


class StrategyStorage:

    def __init__(self, file_path="data/strategies.json"):
        self.file_path = Path(file_path)

        # Create the parent directory if it doesn't exist
        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    def save(self, strategies: list[dict]) -> None:

        with open(
            self.file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                strategies,
                file,
                indent=4,
                ensure_ascii=False
            )

    def load(self) -> list[dict]:

        if not self.file_path.exists():
            return []

        with open(
            self.file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)