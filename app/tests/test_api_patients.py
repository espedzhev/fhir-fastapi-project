import json
from typing import AsyncIterator
from unittest import mock

import fakeredis
import httpx
import pytest
import pytest_asyncio
from app.db.redis import get_redis
from app.main import app
from redis import asyncio as redis


def create_patient_data() -> list:
    return [
        {
            "id": "1",
            "name": [{"given": ["John"], "family": "Doe"}],
            "gender": "male",
            "birthDate": "1980-01-01",
            "address": [{"text": "123 Main St, Anytown, UK"}],
            "telecom": [{"value": "555-1234"}],
        },
        {
            "id": "2",
            "name": [{"given": ["Jane"], "family": "Doe"}],
            "gender": "female",
            "birthDate": "1990-05-15",
            "address": [{"text": "456 Oak St, Anytown, USA"}],
            "telecom": [{"value": "555-5678"}],
        },
        {
            "id": "3",
            "name": [{"given": ["Alice"], "family": "Smith"}],
            "gender": "female",
            "birthDate": "1975-09-23",
            "address": [{"text": "789 Pine St, Othertown, JP"}],
            "telecom": [{"value": "555-8765"}],
        },
    ]


async def add_patients_to_redis(redis_client: redis.Redis) -> None:
    patient_data_list = create_patient_data()

    for patient_data in patient_data_list:
        await redis_client.set(f"Patient:{patient_data['id']}", json.dumps(patient_data))


@pytest_asyncio.fixture
async def redis_client() -> AsyncIterator[redis.Redis]:
    async with fakeredis.FakeAsyncRedis() as client:
        yield client


@pytest_asyncio.fixture
async def app_client(redis_client: redis.Redis) -> AsyncIterator[httpx.AsyncClient]:
    async def get_redis_override() -> redis.Redis:
        return redis_client

    transport = httpx.ASGITransport(app=app)  # type: ignore[arg-type] # https://github.com/encode/httpx/issues/3111
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as app_client:
        with mock.patch.dict(app.dependency_overrides, {get_redis: get_redis_override}):
            yield app_client


@pytest.mark.asyncio
async def test_get_patients_empty(app_client: httpx.AsyncClient) -> None:
    response = await app_client.get("/api/v1/patients")
    assert response.status_code == 200
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_get_specific_patient_with_error(app_client: httpx.AsyncClient) -> None:
    response = await app_client.get("/api/v1/patient/1")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_add_patient_and_retrieve(
    app_client: httpx.AsyncClient,
    redis_client: redis.Redis,
) -> None:
    await add_patients_to_redis(redis_client)

    response = await app_client.get("/api/v1/patients/1")
    assert response.status_code == 200

    data = json.loads(response.json())
    assert data["id"] == "1"
    assert data["name"][0]["family"] == "Doe"


@pytest.mark.asyncio
async def test_get_patients_html(
    app_client: httpx.AsyncClient,
    redis_client: redis.Redis,
) -> None:
    await add_patients_to_redis(redis_client)

    response = await app_client.get("/api/v1/patients-htmx")
    assert response.status_code == 200
    assert "/api/v1/patients-htmx/1" in response.text


@pytest.mark.asyncio
async def test_main_page(app_client: httpx.AsyncClient) -> None:
    response = await app_client.get("/")
    assert response.status_code == 200
    assert "/api/v1/patients-htmx" in response.text
