from fastapi import APIRouter
from starlette.responses import JSONResponse

router = APIRouter()


@router.get("/")
async def health_check():
    return JSONResponse(content={
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    })
