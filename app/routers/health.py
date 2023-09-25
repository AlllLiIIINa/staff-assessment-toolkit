from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.db.db import get_postgresql_db, get_redis_db

router = APIRouter()


@router.get("/")
async def health_check():
    return JSONResponse(content={
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    })


@router.get("/check_postgresql")
async def check_postgresql():
    try:
        engine = await get_postgresql_db()
        async with AsyncSession(engine) as session:
            async with session.begin():
                result = await session.execute(text("SELECT 1"))
                if result.scalar() == 1:
                    return JSONResponse(content={
                        "status_code": 200,
                        "detail": "PostgreSQL is healthy",
                        "result": "working"
                    })
                else:
                    raise HTTPException(status_code=500, detail="PostgreSQL connection is not healthy")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking PostgreSQL connection: {e}")


@router.get("/check_redis")
async def check_redis():
    try:
        redis = await get_redis_db()
        async with redis as redis:
            await redis.execute_command("SET", "test_key", "test_value")
            response = await redis.execute_command("GET", "test_key")
            if response == b'test_value':
                return JSONResponse(content={
                    "status_code": 200,
                    "detail": "Redis is healthy",
                    "result": "working"
                })
            else:
                raise HTTPException(status_code=500, detail="Redis connection is not healthy")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking Redis connection: {e}")
