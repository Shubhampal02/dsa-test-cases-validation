import json
from pathlib import Path

source = Path("output/all_200_generated_test_cases.recovered.json")
destination = Path("output/all_200_generated_test_cases.resolved.json")

data = json.loads(source.read_text(encoding="utf-8"))
cases = data["test_cases"] if isinstance(data, dict) else data

def minimum_cost(nums, k, dist):
    if k == 1:
        if not nums:
            raise ValueError("Empty nums")
        return nums[0]

    choose = k - 1
    window_size = dist + 1
    values = nums[1:]

    if choose > window_size or choose > len(values):
        raise ValueError("Infeasible k/dist constraints")

    best = None
    for start in range(len(values) - window_size + 1):
        window = values[start:start + window_size]
        cost = nums[0] + sum(sorted(window)[:choose])
        if best is None or cost < best:
            best = cost

    if best is None:
        raise ValueError("No feasible window")
    return best

resolved = 0
unresolved = []

for case in cases:
    if case.get("output") is not None:
        continue

    name = case.get("problem_name")
    inp = case.get("input", {})
    case_id = case.get("test_case_id", "")

    try:
        if name == "Flatten Binary Tree to Linked List":
            if inp.get("tree") is not None:
                raise ValueError("Tree representation needs inspection")
            result = None

        elif name == "Second Highest Salary":
            salaries = inp.get("salaries", [])
            unique = sorted(set(salaries), reverse=True)
            result = unique[1] if len(unique) >= 2 else None

        elif name == "Divide an Array Into Subarrays With Minimum Cost II":
            result = minimum_cost(
                inp["nums"], inp["k"], inp["dist"]
            )

        else:
            raise ValueError("No supported deterministic calculation")

        case["output"] = result
        case["output_status"] = "candidate_needs_validation"
        resolved += 1

    except Exception as exc:
        case["output_status"] = "unresolved"
        case["output_issue"] = str(exc)
        unresolved.append({
            "problem": name,
            "test_case_id": case_id,
            "issue": str(exc),
        })

destination.write_text(
    json.dumps(data, indent=2, ensure_ascii=False),
    encoding="utf-8",
)

print("Candidate outputs added:", resolved)
print("Still unresolved:", len(unresolved))
for item in unresolved:
    print(item)
print("Saved new file:", destination)
print("Original recovered file preserved:", source.exists())
print("No database changes made.")
