from datetime import datetime
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import is_abs_url
from .extract import resolve_thumb_url


def transform_for_categories(raw_rows: list[dict]) -> list[dict]:
    print("Transforming for categories...")
    seoul_now = datetime.now(ZoneInfo("Asia/Seoul"))
    out = []
    seen = set()  # category_id 중복 방지
    for r in raw_rows:
        cid = (r.get("categoryId") or "").strip()
        ctype = (r.get("categoryType") or "").strip()
        cvalue = (r.get("categoryValue") or "").strip()
        posterImageUrl = (r.get("posterImageUrl") or "").strip()
        cap_at = seoul_now.isoformat()
        # 필수 검증
        if not cid or not ctype or not cvalue:
            continue

        key = cid
        if key in seen:
            continue
        seen.add(key)

        out.append({
            "id": cid,
            "created_at": cap_at,
            "categoryValue": cvalue,
            "post_url": posterImageUrl
            
            ############### 추가 필드 필요시 여기에
            # updated_at은 DB default now()
        })
    return out


def transform_for_category_totals(raw_rows: list[dict]) -> list[dict]:
    print("Transforming for categories...")
    seoul_now = datetime.now(ZoneInfo("Asia/Seoul"))
    out = []
    seen = set()  # category_id 중복 방지
    for r in raw_rows:
        cid = (r.get("categoryId") or "").strip()
        ctype = (r.get("categoryType") or "").strip()
        cvalue = (r.get("categoryValue") or "").strip()
        openLiveCount = int(r.get("openLiveCount") or 0)
        concurrentUserCount = int(r.get("concurrentUserCount") or 0)
        cap_at = seoul_now.isoformat()
        # 필수 검증
        if not cid or not ctype or not cvalue:
            continue

        key = cid
        if key in seen:
            continue
        seen.add(key)

        out.append({
            "categoryId": cid,
            "openLiveCount": max(openLiveCount, 0),
            "concurrentUserCount": max(concurrentUserCount, 0),
            "captured_at": cap_at
            ############### 추가 필드 필요시 여기에
            # updated_at은 DB default now()
        })
    return out


def transform_for_current_top_streams(raw_rows: list[dict]) -> list[dict]:
    print("Transforming for current_top_streams...")
    seoul_now = datetime.now(ZoneInfo("Asia/Seoul"))
    out = []
    seen = set()  # (category_id, rank)
    for r in raw_rows.values():
        cid = (r.get("categoryId") or "").strip()
        rank = int(r.get("rank") or 0)
        chId = (r.get("channelId") or "").strip()
        title = (r.get("liveTitle") or "").strip()
        UCount = int(r.get("concurrentUserCount") or 0)
        s_url = (r.get("stream_url") or "").strip()
        t_url = (r.get("thumb_url") or "").strip()
        chName = (r.get("channelName") or "").strip()
        chImageUrl = (r.get("channelImageUrl") or "").strip()
        cap_at = seoul_now.isoformat()
        

        # 필수 검증
        if not cid or rank not in (1, 2) or not s_url:
            continue
        if not is_abs_url(s_url):
            continue

        # 썸네일 없으면 원본 유지(필수는 아님)
        if t_url and is_abs_url(t_url):
            t_url = t_url

        key = (cid, rank)
        if key in seen:
            continue
        seen.add(key)

        out.append({
            "categoryId": cid,
            "rank": rank,
            "channelId": chId,  # 고유값 없을 때 규칙 통일
            "liveTitle": title[:512],        # 너무 긴 제목 방지
            "concurrentUserCount": max(UCount, 0),
            "stream_url": s_url,
            "thumb_url": t_url or None,
            "channelName" : chName,
            "channelImageUrl" : chImageUrl,
            "updated_at" : cap_at
            ############### 추가 필드 필요시 여기에
            # updated_at은 DB default now()
        })
    return out

def add_thumb_url_parallel(stream_data: dict[int, dict], workers: int = 8) -> dict[int, dict]:
    keys = list(stream_data.keys())

    def _resolve(k: int):
        tpl = stream_data[k].get("liveImageUrl")
        # 네가 쓰던 해상 로직 그대로 호출 (예: _resolve_thumb_url_debug or resolve_thumb_url)
        url = resolve_thumb_url(tpl)  # 기존 함수명 유지
        return (k, url)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(_resolve, k) for k in keys]
        for fut in as_completed(futs):
            k, url = fut.result()
            if url:
                stream_data[k]["thumb_url"] = url
    return stream_data