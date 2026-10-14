import asyncio

from database import engine
from repositories.test_case_repository import get_all_test_cases
from services.validation_service import ValidationService


async def main():

    try:

        async with engine.connect():
            print("Database connected successfully!")

        test_cases = await get_all_test_cases()

        validation_service = ValidationService()

        print("\nValidation Results:")
        print("-" * 70)

        for test_case in test_cases:

            result = validation_service.validate_test_case(
                test_case
            )

            print(
                result["test_case_id"],
                "=>",
                result["status"],
                "=> Expected:",
                result["expected_output"]
            )

            if result["error"]:
                print(
                    "   Error:",
                    result["error"]
                )

    except Exception as e:

        print("Error:")
        print(e)

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())