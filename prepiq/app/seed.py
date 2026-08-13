"""
One-time seed script — run this after the app is up, so you have data to
actually test against instead of empty tables/collections.

Usage (from the prepiq_run folder, with the containers running):
    docker compose exec api python -m app.seed
"""
import asyncio

from app.db.mongo import questions_collection
from app.db.mysql import SessionLocal
from app.core.security import hash_password
from app.models.user import User

SAMPLE_QUESTIONS = [
    {
        "title": "Sum of Two Numbers",
        "description": "Read two integers a and b on one line, print their sum.",
        "difficulty": "easy",
        "tags": ["math"],
        "topic": "Arrays",
        "test_cases": [
            {"input": "2 3", "expected_output": "5"},
            {"input": "10 20", "expected_output": "30"},
        ],
    },
    {
        "title": "Reverse a String",
        "description": "Read a string, print it reversed.",
        "difficulty": "easy",
        "tags": ["strings"],
        "topic": "Strings",
        "test_cases": [
            {"input": "hello", "expected_output": "olleh"},
            {"input": "abc", "expected_output": "cba"},
        ],
    },
    {
        "title": "Two Pointer Pair Sum",
        "description": "Given a sorted array and a target on the next line, print 'true' if any pair sums to target, else 'false'.",
        "difficulty": "medium",
        "tags": ["two-pointers"],
        "topic": "Two Pointers",
        "test_cases": [
            {"input": "1 2 3 4 6\n10", "expected_output": "true"},
            {"input": "1 2 3 4 6\n100", "expected_output": "false"},
        ],
    },
]


def seed_mysql_admin():
    db = SessionLocal()
    existing = db.query(User).filter(User.email == "admin@prepiq.dev").first()
    if not existing:
        admin = User(
            name="Admin",
            email="admin@prepiq.dev",
            password_hash=hash_password("admin123"),
            role="admin",
        )
        db.add(admin)
        db.commit()
        print("Created admin user -> email: admin@prepiq.dev / password: admin123")
    else:
        print("Admin user already exists, skipping.")
    db.close()


async def seed_mongo_questions():
    count = await questions_collection.count_documents({})
    if count > 0:
        print(f"{count} questions already exist, skipping question seed.")
        return
    await questions_collection.insert_many(SAMPLE_QUESTIONS)
    print(f"Inserted {len(SAMPLE_QUESTIONS)} sample questions.")


if __name__ == "__main__":
    seed_mysql_admin()
    asyncio.run(seed_mongo_questions())
    print("Seeding complete.")
