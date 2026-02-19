from fastapi import FastAPI

from app.api.v1 import auth, index
from app.common.logging import setup_logging
from app.errors import register_all_errors
from app.middlewares.middleware import register_middleware
from app.utils.lifespan import Lifespan


# 전역변수 전달
def get_states():
    return {"state_1": "state_1", "state_2": "state_2"}


def create_app() -> FastAPI:
    """
    앱 함수 실행
    :return:
    """
    version = "v1"
    version_prefix = f"/api/{version}"
    setup_logging()

    # service start, stop event handlers
    lifespan = Lifespan()
    # lifespan.add_startup(initdb)
    lifespan.add_shutdown(print, "Goodbye world")
    lifespan.states = get_states

    app = FastAPI(
        lifespan=lifespan.lifespan,
        title="종달새 PMS",
        description="A REST API for Patient manager System by taeseong",
        version=version,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # 미들웨어 정의
    register_middleware(app)

    # 에러 핸들러 등록
    register_all_errors(app)

    # 라우터 등록
    app.include_router(index.router)
    app.include_router(auth.router, prefix=f"{version_prefix}/auth", tags=["auth"])

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
