import os
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Connect to PostgreSQL
conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    database=os.getenv("POSTGRES_DATABASE"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)

cursor = conn.cursor()

# Read generated JSON file
with open("output/Q001_test_cases.json", "r") as file:
    data = json.load(file)

problem_id = data["problem_id"]

# Insert every test case
for test_case in data["test_cases"]:
    cursor.execute(
        """
        INSERT INTO test_cases.generated_test_cases
        (problem_id, test_case_id, category, pattern, input_data)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            problem_id,
            test_case["test_case_id"],
            test_case["category"],
            test_case["pattern"],
            json.dumps(test_case["input"]),
        ),
    )

conn.commit()

print(f"{len(data['test_cases'])} test cases inserted successfully!")

cursor.close()
conn.close()