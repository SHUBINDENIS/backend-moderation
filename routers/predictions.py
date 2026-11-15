from typing import Annotated

from fastapi import APIRouter, Depends

from dependencies import get_moderation_service
from schemas import PredictionRequest
from services.moderation import ModerationService

router = APIRouter()


@router.post(
    "/predict",
    response_model=bool,
    summary="Проверить объявление на нарушения",
    description="Возвращает true при наличии нарушения и false при его отсутствии.",
    responses={
        400: {"description": "Некорректный JSON, отсутствующее поле или неверное значение"},
        500: {"description": "Внутренняя ошибка сервиса"},
    },
)
async def predict(
    advertisement: PredictionRequest,
    service: Annotated[ModerationService, Depends(get_moderation_service)],
) -> bool:
    return service.predict(advertisement)
