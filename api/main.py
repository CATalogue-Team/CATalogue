from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import cats, users

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

# 路由配置
app.include_router(
    cats.router,
    prefix="/api/v1/cats",
    tags=["猫咪管理"]
)
app.include_router(
    users.router,
    prefix="/api/v1/users",
    tags=["用户管理"]
)

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy"}
