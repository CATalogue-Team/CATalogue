from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers.cats import router as cats_router
from .routers.users import router as users_router

def create_app():
    app = FastAPI(
        title="CATalogue API",
        description="猫咪档案管理平台API",
        version="1.0.0",
        openapi_url="/api/v1/openapi.json"
    )

    # 中间件配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 路由配置 - 移除重复前缀
    app.include_router(
        cats_router,
        prefix="",
        tags=["猫咪管理"]
    )
    app.include_router(
        users_router,
        prefix="",
        tags=["用户管理"]
    )

    @app.get("/api/v1/health")
    async def health_check():
        return {"status": "healthy"}
    
    return app

app = create_app()
