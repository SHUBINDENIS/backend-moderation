from unittest.mock import Mock

import pytest

from repositories.predictions import PredictionRepository
from schemas import PredictionRequest
from services.moderation import ModerationService


@pytest.mark.parametrize(
    ("verified", "images_qty", "expected"),
    [(False, 0, True), (False, 1, False), (True, 0, False), (True, 1, False)],
)
def test_service_decision_and_storage(
    payload: dict, verified: bool, images_qty: int, expected: bool
) -> None:
    repository = Mock(spec=PredictionRepository)
    service = ModerationService(repository)
    payload.update(is_verified_seller=verified, images_qty=images_qty)
    request = PredictionRequest(**payload)
    assert service.predict(request) is expected
    repository.save.assert_called_once_with(100, expected)


def test_service_propagates_storage_failure(payload: dict) -> None:
    repository = Mock(spec=PredictionRepository)
    repository.save.side_effect = RuntimeError("Storage unavailable")
    with pytest.raises(RuntimeError, match="Storage unavailable"):
        ModerationService(repository).predict(PredictionRequest(**payload))
