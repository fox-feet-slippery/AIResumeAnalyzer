import json
import hashlib
from typing import Optional, Any

from app.core.config import settings

# 尝试导入redis，如果失败则使用简化版
try:
    import redis.asyncio as redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    print("警告：未安装redis，将使用内存缓存模式")


class CacheManager:
    def __init__(self):
        self.redis_client = None
        self._memory_cache = {}
    
    async def connect(self):
        if not HAS_REDIS:
            print("使用内存缓存模式")
            return
            
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            await self.redis_client.ping()
            print("Redis连接成功")
        except Exception as e:
            print(f"Redis连接失败: {e}，使用内存缓存模式")
            self.redis_client = None
    
    async def disconnect(self):
        if self.redis_client:
            await self.redis_client.close()
        self._memory_cache.clear()
    
    def _generate_key(self, prefix: str, data: str) -> str:
        hash_value = hashlib.md5(data.encode()).hexdigest()
        return f"{prefix}:{hash_value}"
    
    async def get(self, key: str) -> Optional[Any]:
        # 优先从内存缓存获取
        if key in self._memory_cache:
            return self._memory_cache[key]
            
        if not self.redis_client:
            return None
        try:
            value = await self.redis_client.get(key)
            if value:
                data = json.loads(value)
                # 同步到内存缓存
                self._memory_cache[key] = data
                return data
        except Exception as e:
            print(f"缓存读取失败: {e}")
        return None
    
    async def set(self, key: str, value: Any, ttl: int = None):
        # 保存到内存缓存
        self._memory_cache[key] = value
        
        if not self.redis_client:
            return
        try:
            ttl = ttl or settings.CACHE_TTL
            await self.redis_client.setex(
                key,
                ttl,
                json.dumps(value, ensure_ascii=False)
            )
        except Exception as e:
            print(f"缓存写入失败: {e}")
    
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
