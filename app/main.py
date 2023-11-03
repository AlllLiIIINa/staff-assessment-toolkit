import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import Settings
from app.db.db import get_db
from app.routers import health, user_routers, auth_routers, company_routers

logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

app = FastAPI()
app.db = None

origins = [
    "http://localhost",
    "https://localhost"
    "http://localhost:8000",
    "https://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    app.db = await get_db()


@app.on_event("shutdown")
async def shutdown_event():
    await app.db.close()

app.include_router(health.router)
app.include_router(user_routers.user_router)
app.include_router(auth_routers.auth_router)
app.include_router(company_routers.company_router)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=Settings.ALLOWED_HOST,
        port=Settings.ALLOWED_PORT,
        reload=True
    )
