from services.llm_validator import validate_test_case

problem_statement = (
    "Given a list of stock prices, return the maximum profit "
    "from one buy followed by one sell. Return 0 if no profit is possible."
)

test_case = {
    "test_case_id": "TC_TEST",
    "input": [7, 1, 5, 3, 6, 4],
    "output": 5
}

result = validate_test_case(problem_statement, test_case)
print(result)