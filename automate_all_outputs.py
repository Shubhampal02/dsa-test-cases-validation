
import ast
import hashlib
import json
import os
import re
import sys
import time
from collections import defaultdict, deque
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from psycopg2.extras import Json
from postgres_client import get_connection
from sync_expected_outputs import SOLVERS

import importlib.util

DIVIDE_COST_SOLVER_PATH = Path(
    "output/generated_solvers/"
    "a76438412758d20a24df1e883b0f052ef7b1343c7124e101a8027dfc4727daea.py"
)

def load_divide_cost_solver():
    spec = importlib.util.spec_from_file_location(
        "divide_array_minimum_cost_solver",
        DIVIDE_COST_SOLVER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load repaired Divide Array solver")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.solve


load_dotenv()

DATA_FILE = Path("output/all_200_generated_test_cases.json")
CACHE_DIR = Path("output/generated_solvers")
REPORT_FILE = Path("output/automation_report.json")
RESULTS_FILE = Path("output/calculated_expected_outputs.json")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

MAX_RETRIES = 5
RETRY_DELAY_SECONDS = 35


def json_safe(value):
    """Reject values that cannot be stored as standard JSON."""
    json.dumps(value, allow_nan=False)
    return value


def validate_source(code):
    """Basic source checks; these are not a security sandbox."""
    tree = ast.parse(code)

    if not any(
        isinstance(node, ast.FunctionDef) and node.name == "solve"
        for node in tree.body
    ):
        raise ValueError("Generated source must define solve(data)")

    forbidden_calls = {
        "exec", "eval", "compile", "open", "input", "__import__",
        "breakpoint", "globals", "locals"
    }

    allowed_imports = {
        "math", "collections", "heapq", "bisect",
        "itertools", "functools", "typing"
    }

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            modules = (
                [item.name.split(".")[0] for item in node.names]
                if isinstance(node, ast.Import)
                else [(node.module or "").split(".")[0]]
            )
            if any(module not in allowed_imports for module in modules):
                raise ValueError("Generated source has a disallowed import")

        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in forbidden_calls:
                raise ValueError(
                    f"Generated source uses disallowed call: {node.func.id}"
                )

    return tree


def generate_solver(client, problem_name, examples):
    """Load a cached solver or ask Gemini to create one."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    cache_name = hashlib.sha256(
        problem_name.encode("utf-8")
    ).hexdigest()

    cache_file = CACHE_DIR / f"{cache_name}.py"

    if cache_file.exists():
        code = cache_file.read_text(encoding="utf-8")
        validate_source(code)
        print(f"Using cached solver: {problem_name}")
    else:
        prompt = f"""
Create a Python reference solution for the coding problem:
{problem_name}

Define exactly one function:
def solve(data):
    ...

The input is a Python dictionary matching the JSON examples below.
Return the expected result using JSON-compatible Python values.
Handle the problem's normal input format and edge cases.
Do not guess missing problem requirements.
Do not use external packages, file access, environment variables,
network access, or imports. Use only built-in Python functionality.
Return ONLY Python source code, without Markdown fences.

Input examples:
{json.dumps(examples[:8], ensure_ascii=False)}
"""

        response = None

        for attempt in range(MAX_RETRIES):
            try:
                response = client.models.generate_content(
                    model=MODEL,
                    contents=prompt,
                )
                break

            except Exception as exc:
                message = str(exc)

                is_rate_limit = (
                    "429" in message
                    or "RESOURCE_EXHAUSTED" in message
                )

                if not is_rate_limit or attempt == MAX_RETRIES - 1:
                    raise

                wait_seconds = RETRY_DELAY_SECONDS * (attempt + 1)
                print(
                    f"Rate limit for {problem_name}. "
                    f"Retrying in {wait_seconds} seconds..."
                )
                time.sleep(wait_seconds)

        if response is None or not response.text:
            raise ValueError("Gemini returned an empty response")

        code = response.text.strip()
        code = re.sub(r"^```(?:python)?\s*", "", code)
        code = re.sub(r"\s*```$", "", code)

        validate_source(code)
        cache_file.write_text(code, encoding="utf-8")
        print(f"Generated and cached solver: {problem_name}")

    tree = validate_source(code)

    # This restricts the available built-ins, but it is NOT a secure
    # sandbox for untrusted Python. Review generated source before use.
    safe_builtins = {
        "hasattr": hasattr,
        "__build_class__": __build_class__,
        "abs": abs,
        "__import__": __import__,
        "abs": abs,
        "chr": chr,
        "ord": ord,
        "all": all,
        "any": any,
        "bool": bool,
        "dict": dict,
        "enumerate": enumerate,
        "filter": filter,
        "float": float,
        "int": int,
        "isinstance": isinstance,
        "iter": iter,
        "len": len,
        "list": list,
        "map": map,
        "max": max,
        "min": min,
        "next": next,
        "pow": pow,
        "print": print,
        "range": range,
        "reversed": reversed,
        "round": round,
        "set": set,
        "slice": slice,
        "sorted": sorted,
        "str": str,
        "sum": sum,
        "tuple": tuple,
        "zip": zip,
        "Exception": Exception,
        "ValueError": ValueError,
        "TypeError": TypeError,
        "IndexError": IndexError,
        "KeyError": KeyError,
        "RuntimeError": RuntimeError,
    }

    namespace = {
        "__name__": "__generated_solver__",
        "__builtins__": safe_builtins,
        "deque": deque,
    }

    exec(compile(tree, "<generated-solver>", "exec"), namespace)
    return namespace["solve"]


def load_cases():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Missing test-case file: {DATA_FILE}")

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    if isinstance(data, dict):
        cases = data.get("test_cases")
    else:
        cases = data

    if not isinstance(cases, list):
        raise ValueError(
            f"{DATA_FILE} must contain a list or a test_cases list"
        )

    required = {"problem_id", "test_case_id", "input"}
    for index, case in enumerate(cases):
        missing = required - case.keys()
        if missing:
            raise ValueError(
                f"Case {index} is missing required fields: {sorted(missing)}"
            )

    return cases


def main():
    apply_changes = "--apply" in sys.argv

    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Check your .env file."
        )

    
    all_cases = load_cases()

    conn = get_connection()
    try:
       with conn.cursor() as cursor:
        cursor.execute("""
            SELECT problem_id, test_case_id
            FROM test_cases.generated_test_cases
            WHERE output_data IS NULL
               OR output_data = 'null'::jsonb
        """)
        pending_keys = {
            (str(row[0]), row[1])
            for row in cursor.fetchall()
        }
    finally:
       conn.close()

    cases = [
       case for case in all_cases
       if (
           str(case["problem_id"]),
           case["test_case_id"]
        ) in pending_keys
    ]

    grouped_cases = defaultdict(list)

    for case in cases:
        name = case.get("problem_name")
        if not name:
           name = f"Unknown problem {case['problem_id']}"
        grouped_cases[name].append(case)

    print(f"Total cases in JSON: {len(all_cases)}")
    print(f"Pending database cases: {len(cases)}")


    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    report = {
        "mode": "APPLY" if apply_changes else "DRY RUN",
        "total_cases": len(cases),
        "total_problems": len(grouped_cases),
        "existing_solver_problems": 0,
        "generated_solver_problems": 0,
        "calculated_cases": 0,
        "failed_problems": {},
        "database_rows_missing": 0,
        "already_filled": 0,
        "saved_to_database": 0,
        "pending_outputs": 0,
        "failed_cases": [],
    }

    
   
    calculated_results = []
    successful_problem_names = set()

    # Reuse previously calculated outputs to avoid repeating work.
    previous_results = {}
    if RESULTS_FILE.exists():
        try:
            old_results = json.loads(
                RESULTS_FILE.read_text(encoding="utf-8")
            )
            for item in old_results:
                key = (item["problem_id"], item["test_case_id"])
                previous_results[key] = item
        except (json.JSONDecodeError, KeyError, TypeError):
            previous_results = {}


    for problem_name, problem_cases in grouped_cases.items():
        if problem_name == "Divide an Array Into Subarrays With Minimum Cost II":
            solver = load_divide_cost_solver()
        else:
            solver = SOLVERS.get(problem_name)

        if solver is not None:
            report["existing_solver_problems"] += 1
        else:
            try:
                solver = generate_solver(
                    client,
                    problem_name,
                    [case["input"] for case in problem_cases],
                )
                report["generated_solver_problems"] += 1
            except Exception as exc:
                report["failed_problems"][problem_name] = str(exc)
                print(f"UNRESOLVED: {problem_name}: {exc}")
                continue

        problem_results = []

        for case in problem_cases:
            try:
                if (
                    problem_name == "Random Pick with Weight"
                    and case.get("test_case_id") == "TC_67eb8ab4_003"
                ):
                    report["failed_cases"].append({
                        "problem_name": problem_name,
                        "test_case_id": case.get("test_case_id"),
                        "error": "Invalid test input: empty weights for max_weights_length_10000; regenerate this case.",
                    })
                    print(
                        f"SKIPPED INVALID INPUT: {problem_name} / "
                        f"{case.get('test_case_id')}"
                    )
                    continue

                if (
                    problem_name == "Path with Maximum Gold"
                    and case.get("test_case_id") == "TC_3007c3d4_004"
                ):
                    report["failed_cases"].append({
                        "problem_name": problem_name,
                        "test_case_id": case.get("test_case_id"),
                        "error": "Skipped oversized stress case",
                    })
                    continue

                if problem_name == "Divide an Array Into Subarrays With Minimum Cost II":
                    data = case["input"]
                    nums = data.get("nums")
                    k = data.get("k")
                    dist = data.get("dist")

                    invalid = (
                        not isinstance(nums, list)
                        or not isinstance(k, int)
                        or isinstance(k, bool)
                        or not isinstance(dist, int)
                        or isinstance(dist, bool)
                        or k < 1
                        or k > len(nums)
                        or dist < 0
                        or (k > 1 and dist + 1 < k - 1)
                    )

                    if invalid:
                        report["failed_cases"].append({
                            "problem_name": problem_name,
                            "test_case_id": case.get("test_case_id"),
                            "error": "Invalid test input for k and dist; regenerate or review.",
                        })
                        print(
                            f"SKIPPED INVALID INPUT: {problem_name} / "
                            f"{case.get('test_case_id')}"
                        )
                        continue

                result = solver(case["input"])
                json_safe(result)

                problem_results.append({
                    "problem_id": case["problem_id"],
                    "problem_name": problem_name,
                    "test_case_id": case["test_case_id"],
                    "input": case["input"],
                    "output": result,
                    "solver_source": (
                        "registered"
                        if problem_name in SOLVERS
                        else "generated"
                    ),
                    "review_status": "not_independently_verified",
                })

            except Exception as exc:
                report["failed_cases"].append({
                    "problem_name": problem_name,
                    "test_case_id": case.get("test_case_id"),
                    "error": str(exc),
                })
                report["failed_problems"].setdefault(
                    problem_name,
                    "One or more cases failed; see failed_cases.",
                )
                print(
                    f"FAILED CASE: {problem_name} / "
                    f"{case.get('test_case_id')}: {exc}"
                )

        calculated_results.extend(problem_results)

        # Save progress after each problem
        RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        RESULTS_FILE.write_text(
            json.dumps(calculated_results, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # Save newly calculated outputs to PostgreSQL immediately
        if apply_changes and problem_results:
            conn = get_connection()
            try:
                with conn.cursor() as cursor:
                    for result in problem_results:
                        cursor.execute(
                            """
                            UPDATE test_cases.generated_test_cases
                            SET output_data = %s,
                                review_status = 'not_independently_verified'
                            WHERE problem_id = %s
                              AND test_case_id = %s
                              AND (
                                  output_data IS NULL
                                  OR output_data = 'null'::jsonb
                              )
                            """,
                            (
                                Json(result["output"]),
                                result["problem_id"],
                                result["test_case_id"],
                            ),
                        )
                        report["saved_to_database"] += cursor.rowcount
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

        if problem_results:
            successful_problem_names.add(problem_name)

        report["calculated_cases"] += len(problem_results)

        print(
            f"CALCULATED: {problem_name}: "
            f"{len(problem_results)} cases"
        )


    # Save a local review file even if the database is unavailable.
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_FILE.write_text(
        json.dumps(calculated_results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\n=== AUTOMATION SUMMARY ===")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nCalculated outputs: {RESULTS_FILE}")
    print(f"Report: {REPORT_FILE}")

    if not apply_changes:
        print("\nDRY RUN: no database changes were committed.")
    else:
        print("\nCompleted outputs were committed after each problem.")


if __name__ == "__main__":
    main()

