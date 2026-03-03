from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "智能简历分析系统"
    DEBUG: bool = False
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # 百度千帆AI配置
    QIANFAN_API_KEY: Optional[str] = None
    QIANFAN_SECRET_KEY: Optional[str] = None
    QIANFAN_BASE_URL: str = "https://qianfan.baidubce.com/v2"
    
    # AI模型配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # 阿里云DashScope配置（通义千问）
    DASHSCOPE_API_KEY: Optional[str] = None
    
    # 文件上传配置
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".pdf"}
    
    # 缓存配置
    CACHE_TTL: int = 3600  # 1小时
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
