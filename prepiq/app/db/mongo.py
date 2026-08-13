from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings

mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
mongo_db = mongo_client[settings.MONGO_DB]

# Collections used across the app — import these instead of re-typing names
questions_collection = mongo_db["questions"]
resumes_collection = mongo_db["resumes"]
code_snapshots_collection = mongo_db["code_snapshots"]
interview_logs_collection = mongo_db["ai_interview_logs"]


async def check_mongo_connection() -> bool:
    try:
        # ping is the standard cheap way to verify a live connection
        await mongo_client.admin.command("ping")
        return True
    except Exception:
        return False
