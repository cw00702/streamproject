from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from ..schemas import StreamCard
from ..deps import get_supabase

router = APIRouter(prefix="/top-streams", tags=["top-streams"])

@router.get("", response_model=list[StreamCard])
def get_top_streams(
    categoryId: str = Query(...),
    limit: int = Query(2, ge=1, le=5),
    sb = Depends(get_supabase),
):
    # current_top_streams는 PK("categoryId", rank)
    res = (sb.table("current_top_streams")
             .select("*")
             .eq("categoryId", categoryId)
             .order("rank")
             .limit(limit)
             .execute())
    rows = res.data or []
    return [{
        "rank": r["rank"],
        "categoryId": r["categoryId"],
        "liveTitle": r.get("liveTitle"),
        "channelName": r.get("channelName"),
        "stream_url": r.get("stream_url"),
        "secure_url": r.get("secure_url"),
        "channelImageUrl": r.get("channelImageUrl"),
        "liveImageUrl": r.get("liveImageUrl"),   # 스키마에 없으면 None
        "concurrentUserCount": int(r.get("concurrentUserCount") or 0),
    } for r in rows]
