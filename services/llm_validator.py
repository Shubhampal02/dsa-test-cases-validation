
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def has_large_numeric_array(value):
    """Check whether a numeric array is too large to send in full."""

    if isinstance(value, list):
        if (
            len(value) > 1000
            and all(
                isinstance(item, (int, float))
                and not isinstance(item, bool)
                for item in value
            )
        ):
            return True

        return any(has_large_numeric_array(item) for item in value)

    if isinstance(value, dict):
        return any(
            has_large_numeric_array(item)
            for item in value.values()
        )

    return False


def compact_data(value):
    """Summarize large numeric arrays to limit request size."""

    if isinstance(value, list):
        is_numeric_array = all(
            isinstance(item, (int, float))
            and not isinstance(item, bool)
            for item in value
        )

        if len(value) > 1000 and is_numeric_array:
            return {
                "type": "numeric_array_summary",
                "length": len(value),
                "first_10": value[:10],
                "last_10": value[-10:],
                "min": min(value),
                "max": max(value),
                "note": "The complete array was not provided.",
            }

        return [compact_data(item) for item in value]

    if isinstance(value, dict):
        return {
            key: compact_data(item)
            for key, item in value.items()
        }

    return value


def validate_test_case(problem_statement, test_case):
    """
    Use Groq to generate an expected output and review a DSA test case.

    Returns expected_output, status, and reason.
    """

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return {
            "expected_output": None,
            "status": "Needs Review",
            "reason": "GROQ_API_KEY is missing from .env.",
        }

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )

        # Exact output cannot reliably be calculated from a summary.
        large_input = has_large_numeric_array(test_case)

        payload = {
            "problem_statement": str(problem_statement)[:5000],
            "test_case": compact_data(test_case),
        }

        instructions = """
You are a DSA test-case validation assistant.

Return one valid JSON object with exactly these keys:
"expected_output", "status", "reason".

Allowed status values:
"Valid", "Invalid", "Needs Review".

Rules:
1. Review the problem statement, input format, constraints,
   and expected output requirements.
2. Calculate the expected output by reasoning about the problem.
   Do not use or claim to have executed a reference solution.
3. Use "Valid" when the input is consistent with the constraints
   and you can confidently calculate the expected output.
4. Use "Invalid" only when you identify a concrete input violation.
5. Use "Needs Review" when uncertain or when exact verification
   is impossible from the supplied information.
6. If the complete input is missing or summarized, set
   expected_output to null and status to "Needs Review".
7. For an input that violates constraints, set status to "Invalid".
   Set expected_output to null if it cannot be meaningfully calculated.
8. Keep the reason concise.
9. Return JSON only.

For a stock-profit problem, expected_output should be a number.
For other problems, use the appropriate output type.

Example:
{"expected_output":5,"status":"Valid","reason":"Maximum profit is 6 minus 1, which equals 5."}
"""

        if large_input:
            return {
                "expected_output": None,
                "status": "Needs Review",
                "reason": (
                    "The input is too large to send in full. "
                    "An exact expected output cannot be verified "
                    "from the summarized input."
                ),
            }

        response = client.chat.completions.create(
            model=os.getenv(
                "GROQ_MODEL",
                "openai/gpt-oss-120b",
            ),
            messages=[
                {
                    "role": "system",
                    "content": instructions,
                },
                {
                    "role": "user",
                    "content": (
                        "Calculate the expected output and validate "
                        "this test case. Return JSON only:\n"
                        + json.dumps(payload, separators=(",", ":"))
                    ),
                },
            ],
            temperature=0,
            max_tokens=300,
        )

        content = response.choices[0].message.content

        if not content:
            return {
                "expected_output": None,
                "status": "Needs Review",
                "reason": "The LLM returned an empty response.",
            }

        result = json.loads(content)

        status = result.get("status")
        expected_output = result.get("expected_output")
        reason = result.get("reason", "No reason provided.")

        allowed_statuses = {
            "Valid",
            "Invalid",
            "Needs Review",
        }

        if status not in allowed_statuses:
            return {
                "expected_output": None,
                "status": "Needs Review",
                "reason": "The LLM returned an unrecognized status.",
            }

        if status == "Valid" and expected_output is None:
            return {
                "expected_output": None,
                "status": "Needs Review",
                "reason": (
                    "The LLM marked the case valid but did not "
                    "provide an expected output."
                ),
            }

        return {
            "expected_output": expected_output,
            "status": status,
            "reason": str(reason)[:1000],
        }

    except json.JSONDecodeError:
        print("Groq validation error: Invalid JSON response.")

        return {
            "expected_output": None,
            "status": "Needs Review",
            "reason": "The LLM returned invalid JSON.",
        }

    except Exception as error:
        print(f"Groq validation error: {error}")

        return {
            "expected_output": None,
            "status": "Needs Review",
            "reason": "LLM validation could not be completed.",
        }
