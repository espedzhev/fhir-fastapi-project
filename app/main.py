from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import patients
from .utils.lifespan import load_patient_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Loading patient data..')
    await load_patient_data()
    print('Loading patient data completed')

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(patients.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
