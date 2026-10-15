
import os
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import Json

load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        database=os.getenv("POSTGRES_DATABASE"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        sslmode="require",
    )


def initialize_database():
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE SCHEMA IF NOT EXISTS test_cases;
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS
                test_cases.generated_test_cases (
                    id SERIAL PRIMARY KEY,
                    problem_id VARCHAR(50) NOT NULL,
                    test_case_id VARCHAR(50) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    pattern VARCHAR(100) NOT NULL,
                    input_data JSONB NOT NULL,
                    output_data JSONB
                );
            """)

            cursor.execute("""
                ALTER TABLE test_cases.generated_test_cases
                ADD COLUMN IF NOT EXISTS output_data JSONB;
            """)

            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS
                uq_generated_test_case
                ON test_cases.generated_test_cases
                (problem_id, test_case_id);
            """)

        conn.commit()
        print("PostgreSQL connected successfully!")
        print("Database table is ready.")

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def save_test_cases(problem_id, test_cases):
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            for case in test_cases:
                cursor.execute("""
                    INSERT INTO test_cases.generated_test_cases (
                        problem_id,
                        test_case_id,
                        category,
                        pattern,
                        input_data,
                        output_data
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)

                    ON CONFLICT (problem_id, test_case_id)
                    DO UPDATE SET
                        category = EXCLUDED.category,
                        pattern = EXCLUDED.pattern,
                        input_data = EXCLUDED.input_data,
                        output_data = EXCLUDED.output_data;
                """, (
                    problem_id,
                    case["test_case_id"],
                    case["category"],
                    case["pattern"],
                    Json(case["input"]),
                    Json(case["output"]),
                ))

        conn.commit()
        print(f"Saved {len(test_cases)} test cases for {problem_id}.")

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    initialize_database()
