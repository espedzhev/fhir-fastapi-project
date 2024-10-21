from typing import AsyncIterator
from redis import asyncio as redis


async def get_redis() -> AsyncIterator[redis.Redis]:
    async with redis.from_url("redis://localhost:6379/8", decode_responses=True) as client:
        yield client
