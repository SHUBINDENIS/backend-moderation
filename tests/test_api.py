from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from dependencies import get_moderation_service, get_repository
from services.moderation import ModerationService


@pytest.mark.parametrize(
    ("verified", "images_qty", "expected"),
    [
        (False, 0, True),
        (False, 1, False),
        (False, 10, False),
        (True, 0, False),
        (True, 1, False),
        (True, 10, False),
    ],
)
def test_prediction_truth_table(
    client: TestClient, payload: dict, verified: bool, images_qty: int, expected: bool
) -> None:
    payload.update(is_verified_seller=verified, images_qty=images_qty)
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() is expected
    assert response.text == ("true" if expected else "false")


@pytest.mark.parametrize(
    "field",
    ["seller_id", "is_verified_seller", "item_id", "name", "description", "category", "images_qty"],
)
def test_every_field_is_required(client: TestClient, payload: dict, field: str) -> None:
    payload.pop(field)
    response = client.post("/predict", json=payload)
    assert response.status_code == 400
    assert any(error["loc"] == ["body", field] for error in response.json()["detail"])


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("seller_id", "1"),
        ("seller_id", True),
        ("seller_id", 1.5),
        ("is_verified_seller", "false"),
        ("is_verified_seller", 0),
        ("item_id", "100"),
        ("item_id", False),
        ("item_id", 1.5),
        ("name", 42),
        ("name", []),
        ("description", 42),
        ("description", {}),
        ("category", "10"),
        ("category", True),
        ("category", 1.5),
        ("images_qty", "0"),
        ("images_qty", True),
        ("images_qty", 1.5),
        ("images_qty", -1),
    ],
)
def test_invalid_types_and_negative_images(
    client: TestClient, payload: dict, field: str, value: object
) -> None:
    payload[field] = value
    response = client.post("/predict", json=payload)
    assert response.status_code == 400
    assert any(error["loc"] == ["body", field] for error in response.json()["detail"])


@pytest.mark.parametrize(
    "field",
    ["seller_id", "is_verified_seller", "item_id", "name", "description", "category", "images_qty"],
)
def test_null_is_not_valid(client: TestClient, payload: dict, field: str) -> None:
    payload[field] = None
    assert client.post("/predict", json=payload).status_code == 400


@pytest.mark.parametrize("body", ['{"seller_id":', "not json", "null", "[]", '"text"'])
def test_invalid_json_body(client: TestClient, body: str) -> None:
    response = client.post("/predict", content=body, headers={"Content-Type": "application/json"})
    assert response.status_code == 400


def test_missing_body(client: TestClient) -> None:
    assert client.post("/predict").status_code == 400


def test_unknown_fields_are_rejected(client: TestClient, payload: dict) -> None:
    payload["unexpected_field"] = "value"
    assert client.post("/predict", json=payload).status_code == 400


def test_invalid_input_does_not_reach_service(
    app: FastAPI, client: TestClient, payload: dict
) -> None:
    service = Mock(spec=ModerationService)
    app.dependency_overrides[get_moderation_service] = lambda: service
    payload["images_qty"] = -1
    assert client.post("/predict", json=payload).status_code == 400
    service.predict.assert_not_called()


@pytest.mark.parametrize("origin", ["service", "repository"])
def test_internal_failure_returns_500_without_details(
    app: FastAPI, client: TestClient, payload: dict, origin: str
) -> None:
    if origin == "service":
        dependency = Mock(spec=ModerationService)
        dependency.predict.side_effect = RuntimeError("private failure details")
        app.dependency_overrides[get_moderation_service] = lambda: dependency
    else:
        dependency = Mock()
        dependency.save.side_effect = RuntimeError("private failure details")
        app.dependency_overrides[get_repository] = lambda: dependency

    response = client.post("/predict", json=payload)
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    assert "private failure details" not in response.text


def test_prediction_is_saved(app: FastAPI, client: TestClient, payload: dict) -> None:
    assert client.post("/predict", json=payload).json() is True
    assert app.state.prediction_repository.get(payload["item_id"]) is True
    payload["images_qty"] = 1
    assert client.post("/predict", json=payload).json() is False
    assert app.state.prediction_repository.get(payload["item_id"]) is False


def test_root_example(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_predict_requires_post(client: TestClient) -> None:
    assert client.get("/predict").status_code == 405


def test_documented_contract(client: TestClient) -> None:
    assert client.get("/docs").status_code == 200
    operation = client.get("/openapi.json").json()["paths"]["/predict"]["post"]
    responses = operation["responses"]
    assert responses["200"]["content"]["application/json"]["schema"]["type"] == "boolean"
    assert {"200", "400", "500"} <= set(responses)
    assert "422" not in responses
