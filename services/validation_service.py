from services.reference_service import ReferenceService
from utils.parser import parse_input


class ValidationService:

    def __init__(self):
        self.reference_service = ReferenceService()

    def validate_test_case(self, test_case):

        try:
            problem_id = test_case["problem_id"]
            test_case_id = test_case["test_case_id"]

            # Step 1: Parse input
            input_data = parse_input(
                test_case["input_data"]
            )

            # Step 2: Generate expected output
            expected_output = (
                self.reference_service.generate_expected_output(
                    problem_id,
                    input_data
                )
            )

            # Step 3: Test passed
            return {
                "test_case_id": test_case_id,
                "problem_id": problem_id,
                "input_data": input_data,
                "expected_output": expected_output,
                "status": "VALID",
                "error": None
            }

        except Exception as e:

            return {
                "test_case_id": test_case.get("test_case_id"),
                "problem_id": test_case.get("problem_id"),
                "input_data": test_case.get("input_data"),
                "expected_output": None,
                "status": "INVALID",
                "error": str(e)
            }