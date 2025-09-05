from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime, timedelta, timezone
from ..schemas import TimeSeriesPoint
from ..deps import get_supabase

router = APIRouter(prefix="/timeseries", tags=["timeseries"])

# DB 실제 컬럼명에 맞춰 여기만 수정
TIME_COL = "captured_at"     # ← 기존 snapshotTs 대신 DB의 실제 컬럼
CID_COL  = "categoryId"      # ← 만약 DB가 category_id면 "category_id"로 바꾸세요.

@router.get("", response_model=list[TimeSeriesPoint])
def get_timeseries(
    categoryIds: str = Query(..., description="Comma-separated categoryIds"),
    date_from: Optional[str] = Query(None, description="ISO8601 start (UTC). Defaults to now-7d"),
    date_to: Optional[str] = Query(None, description="ISO8601 end (UTC). Defaults to now"),
    step_minutes: int = Query(30, ge=5, le=120, description="Downsampling (client-side)"),
    sb = Depends(get_supabase)
):
    ids = [s for s in (categoryIds or "").split(",") if s]
    if not ids:
        return []

    now = datetime.now(timezone.utc)
    start = datetime.fromisoformat(date_from) if date_from else now - timedelta(days=7)
    end   = datetime.fromisoformat(date_to)   if date_to   else now

    # 1) DB에서 captured_at 기준으로 범위 조회
    q = (
        sb.table("category_totals")
          .select("*")
          .in_(CID_COL, ids)
          .gte(TIME_COL, start.isoformat())
          .lte(TIME_COL, end.isoformat())
          .order(TIME_COL)
    )
    rows = (q.execute().data) or []

    # 2) (옵션) 간단 다운샘플링
    if step_minutes and rows:
        from collections import defaultdict
        grouped = defaultdict(list)
        for r in rows:
            grouped[r[CID_COL]].append(r)

        out = []
        step = step_minutes
        for cid, arr in grouped.items():
            last_bucket = None
            for r in arr:
                raw_ts = r[TIME_COL]
                ts = raw_ts if isinstance(raw_ts, datetime) else datetime.fromisoformat(str(raw_ts).replace("Z","+00:00"))
                bucket = int(ts.timestamp() // (step * 60))
                if bucket != last_bucket:
                    out.append({
                        "categoryId": cid,
                        "snapshotTs": ts,  # ← 응답 필드는 기존 이름 유지
                        "concurrentUserCount": int(r.get("concurrentUserCount") or 0),
                        "openLiveCount": r.get("openLiveCount"),
                    })
                    last_bucket = bucket
        out.sort(key=lambda x: (x["categoryId"], x["snapshotTs"]))
        return out

    # 3) 다운샘플링 없이 그대로 반환 (응답 필드는 snapshotTs 유지)
    def _to_ts(v):
        return v if isinstance(v, datetime) else datetime.fromisoformat(str(v).replace("Z","+00:00"))
    return [{
        "categoryId": r[CID_COL],
        "snapshotTs": _to_ts(r[TIME_COL]),  # ← DB captured_at → 응답 snapshotTs
        "concurrentUserCount": int(r.get("concurrentUserCount") or 0),
        "openLiveCount": r.get("openLiveCount"),
    } for r in rows]
