# API Design Overview for FHIR Patient Data Service

## Introduction

An overview of the API design for the task

## Requirements
The designs need to include the following:

- **API** that can access the data stored in the JSON file and provide it to a UI in a responsive way

## API Endpoints

### 1. Load Patient Data from JSON File
I initially considered using Django/DRF to define models and use JSON data as fixtures, but instead decided to make a shortcut and load data into Redis. 
There is no plan to add write operations for this application
- **Endpoint**: N/A (automatically triggered on server startup, ~30 sec)
- **Functionality**: Loads patient data from a dataset folder and stores it in Redis for quick access.
- **Data Source**: JSON files containing FHIR-compliant data (FHIR R4B standard).

### 2. Get All Patients in JSON Format
- **Endpoint**: `/api/v1/patients`
- **Method**: `GET`
- **Description**: Returns all patient data in JSON format.
- **Response**: A list of patients, where each patient is represented as a JSON object.
- **TODO**: add pagination

### 3. Get a Specific Patient by ID (JSON Format)
- **Endpoint**: `/api/v1/patients/{patient_id}`
- **Method**: `GET`
- **Description**: Retrieves a specific patient's details using the patient ID.
- **Response**: A JSON object containing the patient details.

### 4. Get All Patients in HTML Format
- **Endpoint**: `/api/v1/patients-htmx`
- **Method**: `GET`
- **Description**: Returns all patient data as HTML table rows.
- **Response**: HTML content with rows for each patient.
- **Usage**: Used for dynamically loading data into the patient page using HTMX.

### 5. Get a Specific Patient by ID (HTML Modal)
- **Endpoint**: `/api/v1/patients-htmx/{patient_id}`
- **Method**: `GET`
- **Description**: Retrieves patient details and formats them in HTML, suitable for displaying in a modal dialog.
- **Response**: HTML content representing patient details.
- **Usage**: This endpoint is used for rendering patient information inside a modal in the frontend web page.

### 6. Main HTML Page for Patients
- **Endpoint**: `/`
- **Method**: `GET`
- **Description**: Provides an HTML page with a table that can dynamically load patient data using HTMX.
- **Response**: HTML page with a button to load patient data and a table to display it.

## Data Flow
- **Startup Data Load**: The patient data is loaded from JSON files during the server's startup. These files are parsed into FHIR-compliant bundles, and relevant data are extracted and stored in Redis.
- **Redis Storage**: Redis is used as the primary data store to cache patient information and allow for rapid data retrieval by the API endpoints.
- **HTML Presentation**: The HTML endpoints use HTMX to dynamically load data into the web page.

## Technologies Used
- **FastAPI**
- **Redis**
- **FHIR Resources Library**: Utilizes the `fhir.resources` library to parse and manage healthcare data according to the FHIR R4B standard.
- **HTMX**: Provides the ability to update parts of the HTML page dynamically, creating an interactive web interface.

## Future Enhancements
- **Appointment Data Integration**: Add support for retrieving appointment details for each patient.
- **Pagination and Filtering**: Introduce pagination for the `/api/v1/patients` endpoint and filtering capabilities to allow more sophisticated queries.
- **User Authentication**: Add authentication and authorization to secure access to patient data.
- **Task Breakdown**: 
  - Load patient data from the dataset and store it in Redis
    - Patient
    - Appointments
    - ...
  - Define the API endpoints
  - Develop HTML templates
  - Add pagination support for the `/api/v1/patients` endpoint
  - Implement authentication and authorization features
  - ...
