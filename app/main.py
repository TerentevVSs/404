import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from config import get_settings
from routers.vectorization import router as vectorization_router

from logging_config import logger

settings = get_settings()


def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        debug=settings.DEBUG,
        version=settings.VERSION,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS or ['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    application.include_router(router=vectorization_router, prefix='/vectors')

    return application


if __name__ == '__main__':
    app = get_application()
    uvicorn.run(app=app, port=settings.APP_PORT)
