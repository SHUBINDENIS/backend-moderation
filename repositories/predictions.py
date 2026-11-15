"""Локальное хранилище для первой домашней работы."""

from threading import Lock
from typing import Protocol


class PredictionRepository(Protocol):
    def save(self, item_id: int, has_violation: bool) -> None: ...


class InMemoryPredictionRepository:
    """Хранит последний результат для объявления в рамках одного процесса."""

    def __init__(self) -> None:
        self._predictions: dict[int, bool] = {}
        self._lock = Lock()

    def save(self, item_id: int, has_violation: bool) -> None:
        with self._lock:
            self._predictions[item_id] = has_violation

    def get(self, item_id: int) -> bool | None:
        with self._lock:
            return self._predictions.get(item_id)
