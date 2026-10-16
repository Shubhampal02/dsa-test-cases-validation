

      
import json
import os

from dotenv import load_dotenv

from groq import Groq

from app.models.problem import Problem

load_dotenv()



class LLMStrategyGenerator:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
           raise ValueError("GROQ_API_KEY not found in .env")

        self.client = Groq(api_key=api_key)
        self.model = "openai/gpt-oss-120b" 
    
    def generate_strategies_batch(
        self, problems: list[Problem]
    ) -> list[dict]:
        if not problems:
            return []

        problem_data = [
            {
                "problem_id": problem.id,
                "title": problem.title,
                "description": problem.description,
                "constraints": problem.constraints,
                "input_format": problem.input_format,
                "output_format": problem.output_format,
                "examples": problem.examples,
            }
            for problem in problems
        ]

        prompt = f"""
You are a test-strategy analyst for competitive programming problems.

For EVERY problem provided, identify relevant test scenarios.
You are specifying test scenarios, NOT generating actual test inputs.

Return only valid JSON in this exact structure:
{{
  "results": [
    {{
      "problem_id": "exact ID from input",
      "test_strategy": [
        {{
          "category": "edge",
          "pattern": "single_element"
        }}
      ]
    }}
  ]
}}

Allowed categories:
sample, basic, edge, boundary, negative, stress

Rules:
1. Return exactly one result for each input problem.
2. Copy each problem_id exactly as provided.
3. Never mix strategies between different problems.
4. Include only relevant scenarios.
5. Do not invent constraints or assume unsupported input rules.
6. Do not generate actual input values.
7. Do not include explanations or extra fields.
8. Avoid duplicate category and pattern combinations.
9. Return valid JSON only.

Problems:
{json.dumps(problem_data, ensure_ascii=False)}
"""

       
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a test-strategy analyst. "
                        "Follow the user's instructions exactly. "
                        "Return valid JSON only."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format={"type": "json_object"},
        )

        response_text = response.choices[0].message.content

        if not response_text:
            raise ValueError("Groq returned an empty response")

        data = json.loads(response_text)

        results = data.get("results")

        if not isinstance(results, list):
            raise ValueError("Gemini response does not contain a results list")

        # Reject unexpected IDs and duplicate results.
        expected_ids = {problem.id for problem in problems}
        received_ids = set()

        for item in results:
            problem_id = item.get("problem_id")

            if problem_id not in expected_ids:
                raise ValueError(
                    f"Unexpected problem ID in Gemini response: {problem_id}"
                )

            if problem_id in received_ids:
                raise ValueError(
                    f"Duplicate problem ID in Gemini response: {problem_id}"
                )

            if not isinstance(item.get("test_strategy"), list):
                raise ValueError(
                    f"Invalid test_strategy for problem {problem_id}"
                )

            received_ids.add(problem_id)

        # A missing result fails the batch so no problem is silently skipped.
        missing_ids = expected_ids - received_ids

        if missing_ids:
            raise ValueError(
                f"Gemini omitted these problem IDs: {sorted(missing_ids)}"
            )

        return results
