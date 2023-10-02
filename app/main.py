import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import Settings
from app.routers import health, user_routers

logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

app = FastAPI()

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

app.include_router(health.router)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=Settings.ALLOWED_HOST,
        port=Settings.ALLOWED_PORT,
        reload=True
    )
