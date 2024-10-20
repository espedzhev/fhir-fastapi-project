import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path

import redis
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.patient import Patient


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Loading patient data..')
    await load_patient_data(dataset_folder='./dataset')
    print('Loading patient data completed')

    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

r = redis.Redis(host='localhost', port=6379, db=6, decode_responses=True)


async def load_patient_data(dataset_folder: str):
    if r.exists('patients_loaded'):
        return

    for filename in os.listdir(dataset_folder):
        file_path = Path(os.path.join(dataset_folder, filename))
        bundle = Bundle.parse_file(file_path)

        for entry in bundle.entry:
            if entry.resource.resource_type == 'Patient':
                patient = entry.resource

                await asyncio.to_thread(r.set, f"Bundle:{patient.id}", bundle.json())
                await asyncio.to_thread(r.set, f"Patient:{patient.id}", patient.json())

    await asyncio.to_thread(r.set, 'patients_loaded', 'true')

@app.get('/api/v1/patients')
async def get_patients():
    """API endpoint to get all patient data"""
    patient_keys = await asyncio.to_thread(r.keys, 'Patient:*')
    patients = []

    for key in patient_keys:
        patient_data = await asyncio.to_thread(r.get, key)

        if patient_data:
            patients.append(patient_data)

    return patients

@app.get('/api/v1/patients-html', response_class=HTMLResponse)
async def get_patients_html():
    """API endpoint to get all patient data as HTML table rows"""
    patient_keys = await asyncio.to_thread(r.keys, 'Patient:*')
    rows = []

    for key in patient_keys:
        patient_data = await asyncio.to_thread(r.get, key)

        if patient_data:
            patient = Patient.parse_raw(patient_data).dict()
            patient_id = patient.get('id', 'N/A')
            name = patient.get('name', [{}])[0]
            full_name = f"{' '.join(name.get('given', []))} {name.get('family', '')}".strip() if name else 'N/A'
            gender = patient.get('gender', 'N/A')
            birth_date = patient.get('birthDate', 'N/A')

            row = f"""
            <tr>
                <td><a href="#" hx-get="/api/v1/patient-htmx/{patient_id}" hx-target="#patientDetailsModal">{patient_id}</a></td>
                <td><a href="#" hx-get="/api/v1/patient-htmx/{patient_id}" hx-target="#patientDetailsModal">{full_name}</a></td>
                <td>{gender}</td>
                <td>{birth_date}</td>
            </tr>
            """
            rows.append(row)

    return HTMLResponse(content="".join(rows))


@app.get('/api/v1/patient/{patient_id}')
async def get_patient(patient_id: str):
    """API endpoint to get a specific patient by ID"""
    patient_data = await asyncio.to_thread(r.get, f"Patient:{patient_id}")

    if not patient_data:
        raise HTTPException(status_code=404, detail='Patient not found')

    return patient_data


@app.get('/api/v1/patient-htmx/{patient_id}', response_class=HTMLResponse)
async def get_patient_html(patient_id: str):
    patient_data = await asyncio.to_thread(r.get, f"Patient:{patient_id}")

    if not patient_data:
        raise HTTPException(status_code=404, detail='Patient not found')

    patient = Patient.parse_raw(patient_data).dict()
    patient_id = patient.get('id', 'N/A')
    name = patient.get('name', [{}])[0]
    full_name = f"{' '.join(name.get('given', []))} {name.get('family', '')}".strip() if name else 'N/A'
    gender = patient.get('gender', 'N/A')
    birth_date = patient.get('birthDate', 'N/A')

    modal_content = f"""
    <div class="modal">
        <div class="modal-content">
            <span class="close" onclick="document.getElementById('patientDetailsModal').innerHTML = ''">&times;</span>
            <h2>Patient Details</h2>
            <p><strong>ID:</strong> {patient_id}</p>
            <p><strong>Name:</strong> {full_name}</p>
            <p><strong>Gender:</strong> {gender}</p>
            <p><strong>Birth Date:</strong> {birth_date}</p>
        </div>
    </div>
    """
    return HTMLResponse(content=modal_content)


@app.get('/', response_class=HTMLResponse)
async def load_patient_page():
    """HTML page for loading patients in a table using HTMX"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Patient Data</title>
        <script src="https://unpkg.com/htmx.org@1.5.0"></script>
        <style>
            table {
                width: 100%;
                border-collapse: collapse;
            }
            table, th, td {
                border: 1px solid black;
            }
            th, td {
                padding: 10px;
                text-align: left;
            }
            .modal {
                display: block;
                position: fixed;
                z-index: 1;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
            }
            .modal-content {
                background-color: #fefefe;
                margin: 15% auto;
                padding: 20px;
                border: 1px solid #888;
                width: 50%;
            }
            .close {
                color: #aaa;
                float: right;
                font-size: 28px;
                font-weight: bold;
            }
            .close:hover,
            .close:focus {
                color: black;
                text-decoration: none;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <h1>Patient Data</h1>
        <button hx-get="/api/v1/patients-html" hx-target="#patientTableBody" hx-trigger="click">Load Patient Data</button>

        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Gender</th>
                    <th>Birth Date</th>
                </tr>
            </thead>
            <tbody id="patientTableBody">
                <!-- Rows will be inserted here by HTMX -->
            </tbody>
        </table>

        <div id="patientDetailsModal"></div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get('/api/v1/single-patient-debug')
async def get_patients():
    dataset_folder='./dataset'

    for filename in os.listdir(dataset_folder)[:1]:
        file_path = Path(os.path.join(dataset_folder, filename))
        bundle = await asyncio.to_thread(Bundle.parse_file, file_path)

        p = [x for x in bundle.entry if x.resource.resource_type == 'Patient']

        return p[0]
        # return p[0].json()
