from contextlib import asynccontextmanager

from app.db.redis import get_redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import patients
from .utils.lifespan import load_patient_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading patient data..")

    redis_client = None

    async for client in get_redis():
        redis_client = client
        break

    if redis_client:
        await load_patient_data(redis_client)

    print("Loading patient data completed")
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(patients.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
