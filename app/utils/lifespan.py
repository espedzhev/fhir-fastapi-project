import asyncio
import os
from pathlib import Path

from app.db.redis import r
from fhir.resources.R4B.bundle import Bundle


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
