import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from config import get_settings
from routers.checking_fakes import router as checking_fakes_router
from routers.fake_detection_ner_sentiment import router as ner_router
from routers.vectorization import router as vectorization_router

settings = get_settings()


def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
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
    application.include_router(router=checking_fakes_router,
                               prefix='/checking-fakes')
    application.include_router(router=ner_router, prefix='/ner')
    from controllers.parser.mos_ru import main as parser_main
    parser_main()
    return application


if __name__ == '__main__':
    app = get_application()
    uvicorn.run(app=app, port=settings.APP_PORT)
