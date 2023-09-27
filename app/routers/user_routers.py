import logging
from typing import List
from fastapi import HTTPException
from health import router
from app.db.models import User
from app.schemas.user import UserBase
from app.schemas.user import UsersList
from app.schemas.user import UserUpdate


@router.get("/user_get{user_id}", response_model=UserBase)
async def user_get(user_id: str):
    try:
        user = await User.get(user_id)
        logging.info("Getting user processed successfully")
        return user

    except Exception as e:
        logging.error(f"Error retrieving user with ID {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving user with ID {user_id}: {e} ")


@router.put("/user_update{user_id}", response_model=UserUpdate)
async def user_update(user_id: str, user: UserBase):
    try:
        user = await User.update(user_id, **user.dict())
        logging.info("Updating user processed successfully")
        return user

    except Exception as e:
        logging.error(f"Error updating user with ID {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating user with ID {user_id}: {e}")


@router.put("/user_delete{user_id}", response_model=UserBase)
async def user_delete(user_id: str):
    try:
        user = await User.delete(user_id)
        logging.info("Deleting user processed successfully")
        return user

    except Exception as e:
        logging.error(f"Error deleting user with ID {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting user with ID {user_id}: {e}")


@router.post("/user_create", response_model=UserBase)
async def user_signin(user: UserBase):
    try:
        user = await User.create(**user.dict())
        logging.info("Creating user processed successfully")
        return user

    except Exception as e:
        logging.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating user: {e}")


@router.get("/user_list", response_model=List[UsersList])
async def user_list():
    try:
        users = await User.get_all()
        logging.info("Getting user list processed successfully")
        return users

    except Exception as e:
        logging.error(f"Error retrieving user list: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving user list: {e}")
