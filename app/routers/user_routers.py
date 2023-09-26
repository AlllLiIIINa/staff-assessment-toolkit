from fastapi import HTTPException
from app.db.db import engine
from app.db.db import User
from health import router


@router.get("/check_user_table")
async def check_user_table():
    try:
        User.metadata.create_all(bind=engine)
        return {"message": "User table exists"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking User table: {e}")


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
