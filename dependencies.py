from typing import Annotated, cast

from fastapi import Depends, Request

from repositories.predictions import PredictionRepository
from services.moderation import ModerationService


def get_repository(request: Request) -> PredictionRepository:
    return cast(PredictionRepository, request.app.state.prediction_repository)


def get_moderation_service(
    repository: Annotated[PredictionRepository, Depends(get_repository)],
) -> ModerationService:
    return ModerationService(repository)
