from pathlib import Path

p = Path("automate_all_outputs.py")
s = p.read_text()

start = "    # Generated LLM solutions are not independently verified.\n"
end = "    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)\n"

if s.count(start) != 1 or s.count(end) != 1:
    raise SystemExit("Expected section not found exactly once; no changes made.")

a = s.index(start)
b = s.index(end, a)
s = s[:a] + s[b:]
p.write_text(s)
print("Removed old final database-writing block.")
