
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv(Path(__file__).resolve().parent / ".env")

BASE_DIR = Path(__file__).resolve().parent
STRATEGY_FILE = BASE_DIR / "input" / "test_strategies_200.json"
CASES_FILE = BASE_DIR / "output" / "all_200_generated_test_cases.json"
DRAFT_FILE = BASE_DIR / "output" / "problem_statement_drafts.json"

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


def load_problems():
    strategies = json.loads(STRATEGY_FILE.read_text(encoding="utf-8"))
    cases_data = json.loads(CASES_FILE.read_text(encoding="utf-8"))
    cases = cases_data["test_cases"]

    by_id = {}
    for item in strategies:
        by_id[item["problem_id"]] = {
            "problem_id": item["problem_id"],
            "problem_name": item["problem_name"],
            "test_strategy": item.get("test_strategy", []),
        }

    examples_by_id = {}
    for case in cases:
        pid = case["problem_id"]
        if pid in by_id:
            examples_by_id.setdefault(pid, [])
            if len(examples_by_id[pid]) < 3:
                examples_by_id[pid].append({
                    "input": case.get("input"),
                    "output": case.get("output"),
                    "category": case.get("category"),
                    "pattern": case.get("pattern"),
                })

    for pid, problem in by_id.items():
        problem["examples"] = examples_by_id.get(pid, [])

    return by_id


def generate_statement(client, problem):
    prompt = f"""
Draft a clear programming problem statement for a coding challenge.

Problem title: {problem["problem_name"]}

Available test-strategy patterns:
{json.dumps(problem["test_strategy"][:30], ensure_ascii=False)}

Available example inputs and outputs:
{json.dumps(problem["examples"], ensure_ascii=False)}

Requirements:
- Return only the problem statement text.
- Explain the task and input/output meaning clearly.
- Do not invent numeric constraints, function signatures, or special rules
  that are not supported by the title or examples.
- If important details cannot be determined, explicitly mark them as
  "Needs verification" in the statement.
- Do not claim this is the original official wording.
"""
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )
    statement = (response.text or "").strip()
    if not statement:
        raise ValueError("Gemini returned an empty statement")
    return statement


def main():
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY is missing from .env")

    problems = load_problems()
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    drafts = []
    for index, problem in enumerate(problems.values(), start=1):
        try:
            statement = generate_statement(client, problem)
            drafts.append({
                "problem_id": problem["problem_id"],
                "problem_name": problem["problem_name"],
                "problem_statement": statement,
                "status": "draft_needs_review",
            })
            print(f"[{index}/{len(problems)}] Drafted: {problem['problem_name']}")
        except Exception as exc:
            drafts.append({
                "problem_id": problem["problem_id"],
                "problem_name": problem["problem_name"],
                "problem_statement": None,
                "status": "failed",
                "error": str(exc),
            })
            print(f"[{index}/{len(problems)}] Failed: {problem['problem_name']}: {exc}")

        # Gentle delay to reduce the chance of hitting rate limits.
        time.sleep(2)

        # Save progress after every problem so an interruption
        # does not lose all previous drafts.
        DRAFT_FILE.parent.mkdir(parents=True, exist_ok=True)
        DRAFT_FILE.write_text(
            json.dumps(drafts, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    succeeded = sum(item["problem_statement"] is not None for item in drafts)
    print(f"\nDrafted: {succeeded}/{len(problems)}")
    print(f"Failed: {len(problems) - succeeded}")
    print(f"Preview file: {DRAFT_FILE}")


if __name__ == "__main__":
    main()
