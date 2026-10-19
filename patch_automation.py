from pathlib import Path

path = Path("automate_all_outputs.py")
source = path.read_text(encoding="utf-8")

old_skip = '''    for problem_name, problem_cases in grouped_cases.items():
        if problem_name == "Divide an Array Into Subarrays With Minimum Cost II":
            report["failed_problems"][problem_name] = "Temporarily skipped: generated solver hangs; needs repair"
            print(f"SKIPPED: {problem_name} ({len(problem_cases)} cases)")
            continue
        solver = SOLVERS.get(problem_name)
'''

new_skip = '''    for problem_name, problem_cases in grouped_cases.items():
        if problem_name == "Divide an Array Into Subarrays With Minimum Cost II":
            solver = load_divide_cost_solver()
        else:
            solver = SOLVERS.get(problem_name)
'''

if old_skip not in source:
    raise SystemExit("ERROR: Original skip block not found. No changes made.")

import_line = "from sync_expected_outputs import SOLVERS\n"
loader = '''
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

'''

if "def load_divide_cost_solver():" not in source:
    if import_line not in source:
        raise SystemExit("ERROR: Expected import line not found. No changes made.")
    source = source.replace(import_line, import_line + loader, 1)

source = source.replace(old_skip, new_skip, 1)

path.write_text(source, encoding="utf-8")
print("Patched solver loading and removed the hard-coded skip.")
