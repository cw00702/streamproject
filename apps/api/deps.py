from __future__ import annotations
from functools import lru_cache
from pydantic import BaseModel
import os

class Settings(BaseModel):
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    cors_allow_origins: list[str] = (os.getenv("CORS_ALLOW_ORIGINS") or "*").split(",")
    api_prefix: str = os.getenv("API_PREFIX", "/api")
    env: str = os.getenv("ENV", "dev")

@lru_cache
def get_settings() -> Settings:
    s = Settings()
    if not s.supabase_url or not s.supabase_key:
        raise RuntimeError("SUPABASE_URL / SUPABASE_KEY가 설정되지 않았습니다.")
    return s

@lru_cache
def get_supabase():
    # 서버에서만 사용해야 함(키 노출 금지)
    from supabase import create_client
    s = get_settings()
    return create_client(s.supabase_url, s.supabase_key)
