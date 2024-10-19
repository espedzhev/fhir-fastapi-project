from fastapi import FastAPI
from starlette.responses import HTMLResponse

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/hello/{name}/html", response_class=HTMLResponse)
async def read_items():
    patient_list = [{}, {}, {}]
    # Generate HTML table
    html_content = """<html>
    <head><title>Patients List</title></head>
    <body>
    <h2>Patients List</h2>
    <table border="1">
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Birthdate</th>
            <th>Gender</th>
            <th>Address</th>
        </tr>
    """
    for patient in patient_list:
        html_content += f"""<tr>
            <td>{patient.get('id', 'N/A')}</td>
            <td>{patient.get('name', [{'text': 'N/A'}])[0]['text']}</td>
            <td>{patient.get('birthDate', 'N/A')}</td>
            <td>{patient.get('gender', 'N/A')}</td>
            <td>{patient.get('address', [{'text': 'N/A'}])[0]['text']}</td>
        </tr>"""

    html_content += """</table>
    </body>
    </html>"""

    return html_content
