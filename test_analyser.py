
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from upstash_redis import Redis

from app.models.problem import Problem
from app.analyser.problem_analyzer import ProblemAnalyzer

load_dotenv()

# Configuration
BATCH_SIZE = 5
MAX_QUESTIONS = 200

STRATEGIES_FILE = Path("data/strategies.json")
FAILED_FILE = Path("data/failed_questions.json")

# Connect to Upstash Redis
redis = Redis(
    url=os.getenv("UPSTASH_REDIS_REST_URL"),
    token=os.getenv("UPSTASH_REDIS_REST_TOKEN"),
)


def load_json_file(file_path, default):
    if not file_path.exists():
        return default

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json_file(file_path, data):
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def convert_to_problem(record):
    payload = record.get("question_payload", {})

    if isinstance(payload, str):
        payload = json.loads(payload)

    title = payload.get("title", "Untitled Problem")

    constraints = payload.get("constraints", [])
    if not isinstance(constraints, list):
        constraints = [str(constraints)]

    examples = payload.get("examples", [])
    if not isinstance(examples, list):
        examples = []

    return Problem(
        id=record["id"],
        title=title,
        description=payload.get("description", ""),
        constraints=constraints,
        input_format=payload.get("input_format", ""),
        output_format=payload.get("output_format", ""),
        examples=examples,
    )


def is_quota_error(error):
    message = str(error).lower()

    return (
        "429" in message
        or "resource_exhausted" in message
        or "quota exceeded" in message
        or "generate_content_free_tier_requests" in message
    )


def main():
    print("Loading existing results...")

    results = load_json_file(STRATEGIES_FILE, [])
    failures = load_json_file(FAILED_FILE, [])

    # Preserve successful results and avoid duplicate IDs.
    results_by_id = {
        item["problem_id"]: item
        for item in results
        if "problem_id" in item
    }

    failures_by_id = {
        item["problem_id"]: item
        for item in failures
        if "problem_id" in item
    }

    completed_ids = set(results_by_id)

    print(f"Already completed: {len(completed_ids)} questions")

    print("Fetching questions from Redis...")
    raw_data = redis.get("coding_questions:legacy")

    if not raw_data:
        raise ValueError("No data found at coding_questions:legacy")

    if isinstance(raw_data, bytes):
        raw_data = raw_data.decode("utf-8")

    records = json.loads(raw_data)

    active_records = [
        record
        for record in records
        if record.get("status") == "active"
    ][:MAX_QUESTIONS]

    # Keep only questions that don't already have saved results.
    pending_records = [
        record
        for record in active_records
        if record.get("id") not in completed_ids
    ]

    print(f"Questions in target set: {len(active_records)}")
    print(f"Questions remaining: {len(pending_records)}")

    if not pending_records:
        print("All questions in the target set are completed.")
        return

    # Convert the pending Redis records into Problem objects.
    problems = []
    invalid_records = []

    for record in pending_records:
        try:
            problems.append(convert_to_problem(record))
        except Exception as error:
            problem_id = record.get("id", "unknown")

            invalid_records.append(
                {
                    "problem_id": problem_id,
                    "error": f"Could not parse problem: {error}",
                }
            )

    for failure in invalid_records:
        failures_by_id[failure["problem_id"]] = failure

    analyzer = ProblemAnalyzer()

    total_batches = (
        len(problems) + BATCH_SIZE - 1
    ) // BATCH_SIZE

    for start in range(0, len(problems), BATCH_SIZE):
        batch = problems[start:start + BATCH_SIZE]
        batch_number = start // BATCH_SIZE + 1

        print(
            f"\nBatch {batch_number}/{total_batches}: "
            f"{len(batch)} questions"
        )

        try:
            batch_results = analyzer.analyze_many(batch)

            # Save successful results immediately.
            for result in batch_results:
                problem_id = result["problem_id"]
                results_by_id[problem_id] = result

                # Remove an old failure if this question now succeeds.
                failures_by_id.pop(problem_id, None)

            save_json_file(
                STRATEGIES_FILE,
                list(results_by_id.values()),
            )
            save_json_file(
                FAILED_FILE,
                list(failures_by_id.values()),
            )

            print(
                f"Saved {len(batch_results)} results. "
                f"Total completed: {len(results_by_id)}"
            )

        except Exception as error:
            print(f"Batch failed: {error}")

            # Record failures without discarding successful results.
            for problem in batch:
                failures_by_id[problem.id] = {
                    "problem_id": problem.id,
                    "problem_name": problem.title,
                    "error": str(error),
                }

            save_json_file(
                FAILED_FILE,
                list(failures_by_id.values()),
            )

            if is_quota_error(error):
                print(
                    "Gemini quota limit reached. "
                    "Stopping to avoid unnecessary requests."
                )
                break

            print("This batch failed; moving to the next batch.")

        # Small pause between requests; this does not reset daily quota.
        time.sleep(2)

    print("\nProcessing finished.")
    print(f"Successful results: {len(results_by_id)}")
    print(f"Recorded failures: {len(failures_by_id)}")
    print(f"Results file: {STRATEGIES_FILE}")
    print(f"Failures file: {FAILED_FILE}")


if __name__ == "__main__":
    main()
