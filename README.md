# DSA Test Case Generation and Validation

## Overview

This project automates test-case generation, expected-output calculation, database storage, and validation for Data Structures and Algorithms problems.

## Features

- Generate DSA test cases.
- Calculate expected outputs using available solution logic.
- Store and validate test cases in PostgreSQL.
- Check missing expected outputs and problem statements.
- Update database rows whose problem_statement is NULL.
- Run automated tests with pytest.

## Tech Stack

- Python
- PostgreSQL
- psycopg2
- SQLAlchemy
- python-dotenv
- Google GenAI
- pytest

## Setup

Clone the repository and select the project branch:

```bash
git clone -b trupti_19 https://github.com/Shubhampal02/dsa-test-cases-validation.git
cd dsa-test-cases-validation
```

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
```

## Environment Variables

Create a local `.env` file containing `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DATABASE`, `POSTGRES_USER`, and `POSTGRES_PASSWORD`. Use your authorized database credentials. Never commit `.env` or share passwords.

## Important Scripts

- `main.py`: Main generation workflow.
- `calculate_expected_outputs.py`: Expected-output calculation.
- `insert_test_cases.py`: Test-case insertion.
- `check_test_cases.py`: Checks stored test cases.
- `check_missing_outputs.py`: Checks missing outputs.
- `generate_problem_statements.py`: Generates statement drafts.
- `update_problem_statements.py`: Updates missing statements.
- `verify_statement_ids.py`: Verifies statement IDs.

## Problem Statements

The file `output/problem_statement_drafts.json` contains AI-generated drafts. These drafts are not automatically official or verified and should be reviewed. The update script is database-writing code; verify the target database and review its preview before running it. Do not rerun a completed update unnecessarily.

## Run Tests

```bash
python -m pytest tests/
```

Review failures, skipped tests, and uncollected tests separately.

## Git

```bash
git status
git add README.md
git diff --cached --check
git commit -m "Add project README"
git push origin trupti_19
```

Review staged files before committing. Never publish secrets or local virtual environments.
