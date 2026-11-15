import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from repositories.predictions import InMemoryPredictionRepository
from routers.predictions import router

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    application = FastAPI(title="Сервис модерации объявлений", version="1.0.0")
    application.state.prediction_repository = InMemoryPredictionRepository()

    @application.get("/", include_in_schema=False)
    async def root() -> dict[str, str]:
        return {"message": "Hello World"}

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # Отдаём 400 по контракту задания вместо стандартного для FastAPI 422.
        details = [
            {"loc": error["loc"], "msg": error["msg"], "type": error["type"]}
            for error in exc.errors()
        ]
        return JSONResponse(status_code=400, content={"detail": details})

    @application.exception_handler(Exception)
    async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Ошибка обработки запроса", exc_info=(type(exc), exc, exc.__traceback__))
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    application.include_router(router)

    def custom_openapi() -> dict:
        if application.openapi_schema is None:
            schema = get_openapi(
                title=application.title,
                version=application.version,
                routes=application.routes,
            )
            # Документация отражает реальную замену 422 на 400.
            schema["paths"]["/predict"]["post"]["responses"].pop("422", None)
            application.openapi_schema = schema
        return application.openapi_schema

    application.openapi = custom_openapi
    return application


app = create_app()
