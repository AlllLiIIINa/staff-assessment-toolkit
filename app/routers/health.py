from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.db.db import get_db, get_redis

router = APIRouter()


@router.get("/")
async def health_check():
    return JSONResponse(content={
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    })


@router.get("/check_postgresql")
async def check_postgresql(session: AsyncSession = Depends(get_db)):
    try:
        result = await session.execute(text("SELECT 1"))

        if result.scalar() == 1:
            return JSONResponse(content={"status_code": 200, "detail": "PostgreSQL is healthy", "result": "working"})
        else:
            raise HTTPException(status_code=500, detail="PostgreSQL connection is not healthy")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking PostgreSQL connection: {e}")


@router.get("/check_redis")
async def check_redis(redis=Depends(get_redis)):
    try:
        await redis.execute_command("SET", "test_key", "test_value")
        result = await redis.execute_command("GET", "test_key")

        if result == b'test_value':
            return JSONResponse(content={"status_code": 200, "detail": "Redis is healthy", "result": "working"})
        else:
            raise HTTPException(status_code=500, detail="Redis connection is not healthy")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking Redis connection: {e}")
