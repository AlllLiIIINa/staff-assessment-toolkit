from fastapi import HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from app.db.db import get_db
from health import router


# @router.get("/check_user_table")
# async def check_user_table(session: AsyncSession = Depends(get_db)):
#     try:
#         result = await session.execute(text("SELECT 1 FROM users LIMIT 1"))
#
#         if result.scalar() == 1:
#             return JSONResponse(content={"status_code": 200, "detail": "User table exist", "result": "working"})
#         else:
#             raise HTTPException(status_code=500, detail="User table do not exist")
#
#     except Exception as e:
#
#         raise HTTPException(status_code=500, detail=f"Error checking PostgreSQL connection: {e}")


@router.get("/user_get")
async def user_get():
    pass


@router.get("/user_update")
async def user_update():
    pass


@router.get("/user_signin")
async def user_signin():
    pass


@router.get("/user_signup")
async def user_signup():
    pass


@router.get("/user_list")
async def user_list():
    pass


@router.get("/user_detail")
async def user_detail():
    pass
