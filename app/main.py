import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/")
async def health_check():
    response_content = {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }
    return JSONResponse(content=response_content)

if __name__ == "__main__":
    os.system("uvicorn app.main:app --reload")
