import redis.asyncio as redis

from app.core.config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True,  # get str back instead of bytes
)


async def check_redis_connection() -> bool:
    try:
        return await redis_client.ping()
    except Exception:
        return False
