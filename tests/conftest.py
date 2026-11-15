from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from main import create_app


@pytest.fixture
def app() -> FastAPI:
    return create_app()


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    # Так проверяется HTTP-ответ 500, а не повторный выброс ошибки в сам тест.
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture
def payload() -> dict:
    return {
        "seller_id": 1,
        "is_verified_seller": False,
        "item_id": 100,
        "name": "Стол",
        "description": "Письменный стол в хорошем состоянии",
        "category": 10,
        "images_qty": 0,
    }
