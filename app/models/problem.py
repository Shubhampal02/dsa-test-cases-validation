from dataclasses import dataclass


@dataclass
class Problem:
    id: str
    title: str
    description: str
    constraints: list[str]
    input_format: str
    output_format: str
    examples: list[dict]