import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    database=os.getenv("POSTGRES_DATABASE"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)

try:
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT
                problem_id,
                test_case_id,
                category,
                pattern,
                CASE
                    WHEN jsonb_typeof(input_data) = 'array'
                    THEN jsonb_array_length(input_data)
                    ELSE NULL
                END AS input_length
            FROM test_cases.generated_test_cases
            WHERE problem_id = 'Q001'
            ORDER BY test_case_id;
        """)

        rows = cursor.fetchall()

    print("Q001 test cases in Aiven:")
    print("Total:", len(rows))
    print()

    for row in rows:
        print(
            f"{row[1]} | "
            f"{row[2]} | "
            f"{row[3]} | "
            f"Input length: {row[4] if row[4] is not None else 'Not an array'}"
        )
finally:
    conn.close()
