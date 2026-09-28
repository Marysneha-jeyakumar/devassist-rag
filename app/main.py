from fastapi import FastAPI

from app.api.routes import router

from app.core.config import get_settings

from app.core.logging import setup_logging


setup_logging()


settings = get_settings()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)


app.include_router(router)