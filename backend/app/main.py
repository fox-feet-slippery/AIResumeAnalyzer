from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import resume, matching
from app.core.config import settings
from app.core.cache import cache_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await cache_manager.connect()
    yield
    # Shutdown
    await cache_manager.disconnect()


app = FastAPI(
    title="智能简历分析系统",
    description="AI赋能的简历解析、评分与匹配系统",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(resume.router, prefix="/api/resume", tags=["简历管理"])
app.include_router(matching.router, prefix="/api/matching", tags=["岗位匹配"])


@app.get("/")
async def root():
    return {"message": "智能简历分析系统 API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
