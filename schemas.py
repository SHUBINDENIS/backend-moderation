"""Контракт входных данных HTTP API."""

from pydantic import BaseModel, ConfigDict, Field


class PredictionRequest(BaseModel):
    """Все семь полей обязательны; JSON-типы не преобразуются автоматически."""

    model_config = ConfigDict(strict=True, extra="forbid")

    seller_id: int
    is_verified_seller: bool
    item_id: int
    name: str
    description: str
    category: int
    images_qty: int = Field(ge=0)
