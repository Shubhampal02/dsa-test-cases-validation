
import os
import json
from dotenv import load_dotenv
from upstash_redis import Redis

load_dotenv()

redis = Redis(
    url=os.getenv("UPSTASH_REDIS_REST_URL"),
    token=os.getenv("UPSTASH_REDIS_REST_TOKEN")
)

question_id = "1c524f96-31af-46aa-947d-7117c243951a"

try:
    print("Testing Redis connection...")
    print("Redis ping:", redis.ping())

    print("Fetching legacy question data...")
    raw_data = redis.get("coding_questions:legacy")

    if not raw_data:
        print("No data found at coding_questions:legacy")
        raise SystemExit(1)

    questions = json.loads(raw_data)
    print("Total legacy records:", len(questions))

    for question in questions:
        if question.get("id") == question_id:
            print("\nQuestion found:")
            print(json.dumps(question, indent=2))
            break
    else:
        print(f"\nQuestion ID not found: {question_id}")

except Exception as e:
    print("Error:", repr(e))