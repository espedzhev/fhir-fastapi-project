import os
from pathlib import Path
from typing import Any

from fhir.resources.R4B.bundle import Bundle
from redis import asyncio as redis

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATASET_FOLDER = BASE_DIR / "dataset"


async def load_patient_data(redis_client: redis.Redis) -> Any:
    if await redis_client.exists("patients_loaded"):
        return

    for filename in os.listdir(DATASET_FOLDER):
        file_path = Path(DATASET_FOLDER / filename)
        bundle = Bundle.parse_file(file_path)

        for entry in bundle.entry:
            if entry.resource.resource_type == "Patient":
                patient = entry.resource
                # await redis_client.set(f'Bundle:{patient.id}', bundle.json())
                await redis_client.set(f"Patient:{patient.id}", patient.json())

    await redis_client.set("patients_loaded", "true")
