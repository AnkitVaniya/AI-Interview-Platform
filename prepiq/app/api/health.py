from fastapi import APIRouter

from app.db.mysql import check_mysql_connection
from app.db.mongo import check_mongo_connection

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    mysql_ok = check_mysql_connection()
    mongo_ok = await check_mongo_connection()

    all_ok = mysql_ok and mongo_ok

    return {
        "status": "ok" if all_ok else "degraded",
        "services": {
            "mysql": "up" if mysql_ok else "down",
            "mongodb": "up" if mongo_ok else "down",
        },
    }
