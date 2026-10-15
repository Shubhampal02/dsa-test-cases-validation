
import json
import os

from models.test_strategy import TestStrategy
from generators.array_generator import ArrayGenerator
from services.reference_solution import calculate_expected_output
from postgres_client import initialize_database, save_test_cases


def main():
    os.makedirs("output", exist_ok=True)

    # Initialize the PostgreSQL database and table
    initialize_database()

    generator = ArrayGenerator()

    for problem_id in TestStrategy.strategies:
        print(f"\nGenerating test cases for {problem_id}")

        strategies = TestStrategy.get_strategy(problem_id)

        if not strategies:
            print(f"No strategies found for {problem_id}")
            continue

        # This reference solution currently supports Q001 only.
        if problem_id != "Q001":
            print(
                f"No reference solution configured for {problem_id}. "
                "Skipping this problem."
            )
            continue

        test_cases = []

        for index, strategy in enumerate(strategies, start=1):
            size = 5
            min_value = 0
            max_value = 100000

            # Generate test input using your existing generator
            generated_input = generator.generate(
                strategy["pattern"],
                size,
                min_value,
                max_value
            )

            # Calculate the expected output
            expected_output = calculate_expected_output(generated_input)

            test_cases.append({
                "test_case_id": f"TC{index:03d}",
                "category": strategy["category"],
                "pattern": strategy["pattern"],
                "input": generated_input,
                "output": expected_output
            })

        # Save generated test cases to JSON
        json_data = {
            "problem_id": problem_id,
            "test_cases": test_cases
        }

        output_file = f"output/{problem_id}_test_cases.json"

        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(json_data, file, indent=2)

        print(f"Generated {len(test_cases)} test cases")
        print(f"Saved to {output_file}")

        # Save inputs and expected outputs to PostgreSQL
        save_test_cases(problem_id, test_cases)

        print("Expected outputs saved to PostgreSQL.")

        # Display each input and expected output
        for case in test_cases:
            print(
                f"{case['test_case_id']} | "
                f"Input: {case['input']} | "
                f"Expected output: {case['output']}"
            )


if __name__ == "__main__":
    main()
