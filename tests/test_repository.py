from main import create_app
from repositories.predictions import InMemoryPredictionRepository


def test_repository_preserves_both_boolean_values() -> None:
    repository = InMemoryPredictionRepository()
    assert repository.get(100) is None
    repository.save(100, True)
    repository.save(200, False)
    assert repository.get(100) is True
    assert repository.get(200) is False
    repository.save(100, False)
    assert repository.get(100) is False


def test_applications_do_not_share_storage() -> None:
    first, second = create_app(), create_app()
    first.state.prediction_repository.save(100, True)
    assert second.state.prediction_repository.get(100) is None
