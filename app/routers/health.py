import logging
from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from app.db.db import get_db, get_redis
from app.depends.exceptions import CustomException, ErrorStartingApp, ErrorPostgresSQL, ErrorRedis

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    try:
        return JSONResponse(content={
            "status_code": 200,
            "detail": "ok",
            "result": "working"
        })

    except Exception as e:
        logging.error(f"Error starting app: {e}")
        raise ErrorStartingApp(e)


@router.get("/check_postgresql")
async def check_postgresql(session: AsyncSession = Depends(get_db)):
    try:
        result = await session.execute(text("SELECT 1"))

        if result.scalar() == 1:
            logging.info("Postgresql check processed successfully")
            return JSONResponse(content={"status_code": 200, "detail": "PostgresSQL is healthy", "result": "working"})

    except Exception as e:
        logging.error(f"Error checking PostgresSQL connection: {e}")
        raise ErrorPostgresSQL(e)


@router.get("/check_redis")
async def check_redis(redis=Depends(get_redis)):
    try:
        await redis.execute_command("SET", "test_key", "test_value")
        result = await redis.execute_command("GET", "test_key")

        if result == b'test_value':
            logging.info("Redis check processed successfully")
            return {"status_code": 200, "detail": "Redis is healthy", "result": "working"}

    except CustomException as e:
        logging.error(f"Error checking Redis connection: {e}")
        raise ErrorRedis(e)
