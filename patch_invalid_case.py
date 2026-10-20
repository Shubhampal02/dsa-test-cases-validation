from pathlib import Path

path = Path("automate_all_outputs.py")
source = path.read_text(encoding="utf-8")

anchor = '''                result = solver(case["input"])
                json_safe(result)
'''

replacement = '''                if problem_name == "Divide an Array Into Subarrays With Minimum Cost II":
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
'''

if source.count(anchor) != 1:
    raise SystemExit(
        f"Expected exactly one insertion point, found {source.count(anchor)}. No changes made."
    )

if "Invalid test input for k and dist; regenerate or review." in source:
    raise SystemExit("Validation guard already exists. No changes made.")

path.write_text(source.replace(anchor, replacement, 1), encoding="utf-8")
print("Added invalid-input guard inside the case loop.")
