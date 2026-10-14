from sqlalchemy import text
from database import AsyncSessionLocal


async def get_all_test_cases():

    async with AsyncSessionLocal() as session:

        query = text("""
            SELECT
                id,
                problem_id,
                test_case_id,
                category,
                pattern,
                input_data
            FROM test_cases.generated_test_cases
            ORDER BY id
        """)

        result = await session.execute(query)

        return result.mappings().all()