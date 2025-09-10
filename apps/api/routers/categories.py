from __future__ import annotations
from fastapi import APIRouter, Depends
from ..schemas import CategoryOption
from ..deps import get_supabase, get_settings

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("", response_model=list[CategoryOption])
def list_categories(sb = Depends(get_supabase), settings = Depends(get_settings)):
    # 컬럼 "categoryValue"는 케이스 민감 → select("*")로 받고 파이썬에서 매핑
    res = sb.table("categories").select("*").execute()
    data = res.data or []
    data.sort(key=lambda r: (r.get("categoryValue") or "").lower())
    return [{"id": r["id"],
            "label": r.get("categoryValue") or r["id"],
            "post_url":r.get("post_url")}
            for r in data]
