"""
简化版缓存管理器（不依赖Redis）
"""
from typing import Optional, Any
import hashlib


class CacheManager:
    """内存缓存管理器"""
    
    def __init__(self):
        self._cache = {}
        self.redis_client = None
    
    async def connect(self):
        """连接缓存（内存模式无需连接）"""
        print("使用内存缓存模式")
    
    async def disconnect(self):
        """断开连接"""
        self._cache.clear()
    
    def _generate_key(self, prefix: str, data: str) -> str:
        hash_value = hashlib.md5(data.encode()).hexdigest()
        return f"{prefix}:{hash_value}"
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        return self._cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: int = None):
        """设置缓存"""
        self._cache[key] = value
    
    async def get_resume_cache(self, file_hash: str) -> Optional[dict]:
        key = self._generate_key("resume", file_hash)
        return await self.get(key)
    
    async def set_resume_cache(self, file_hash: str, data: dict):
        key = self._generate_key("resume", file_hash)
        await self.set(key, data)
    
    async def get_matching_cache(self, resume_hash: str, job_desc: str) -> Optional[dict]:
        combined = f"{resume_hash}:{job_desc}"
        key = self._generate_key("matching", combined)
        return await self.get(key)
    
    async def set_matching_cache(self, resume_hash: str, job_desc: str, data: dict):
        combined = f"{resume_hash}:{job_desc}"
        key = self._generate_key("matching", combined)
        await self.set(key, data)


cache_manager = CacheManager()
