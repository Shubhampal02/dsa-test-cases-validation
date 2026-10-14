from reference_solutions.solution_registry import REFERENCE_SOLUTIONS


class ReferenceService:

    def generate_expected_output(self, problem_id, input_data):

        if problem_id not in REFERENCE_SOLUTIONS:
            raise ValueError(
                f"No reference solution found for {problem_id}"
            )

        solution = REFERENCE_SOLUTIONS[problem_id]

        return solution(input_data)