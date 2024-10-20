import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fhir.resources.R4B.bundle import Bundle

from.routers import patients
from app.db.redis import r


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Loading patient data..')
    await load_patient_data(dataset_folder='./dataset')
    print('Loading patient data completed')

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


async def load_patient_data(dataset_folder: str):
    if r.exists('patients_loaded'):
        return

    for filename in os.listdir(dataset_folder):
        file_path = Path(os.path.join(dataset_folder, filename))
        bundle = Bundle.parse_file(file_path)

        for entry in bundle.entry:
            if entry.resource.resource_type == 'Patient':
                patient = entry.resource

                # await asyncio.to_thread(r.set, f"Bundle:{patient.id}", bundle.json())
                await asyncio.to_thread(r.set, f"Patient:{patient.id}", patient.json())

    await asyncio.to_thread(r.set, 'patients_loaded', 'true')
