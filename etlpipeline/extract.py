from .utils import normalize
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import requests
from .config import HEADERS, DEFAULT_TIMEOUT, CATEGORY_STREAMS_BASE, category_streams_url,BASE, IMG_HEADERS, TYPE_CANDIDATES, EXT_CANDIDATES

from pprint import pprint

_thread_local = threading.local()
def _get_session() -> requests.Session:
    s = getattr(_thread_local, "s", None)
    if s is None:
        s = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=32, pool_maxsize=32, max_retries=0)
        s.mount("http://", adapter)
        s.mount("https://", adapter)
        _thread_local.s = s
    return s

class FetchError(Exception): pass

def has_live_for_category(categoryType: str, categoryId: str, timeout=8) -> bool:
    print(f"Checking live existence for {categoryId}...")
    base = category_streams_url(categoryType, categoryId)  # v2
    r = requests.get(base, params={"size": 1}, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    items = (r.json().get("content") or {}).get("data") or []
    print("check to missing item :",items, len(items))
    return len(items) > 0

# extract.py
def compute_totals_via_v2(category_type: str, category_id: str, page_size=100, timeout=10):
    base = category_streams_url(category_type, category_id)
    open_cnt = 0
    conc_sum = 0

    # v2 페이지 메타를 모르니, 넉넉히 한 번 크게 요청 (필요시 반복 로직 추가)
    r = requests.get(base, params={"size": page_size}, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    items = (r.json().get("content") or {}).get("data") or []
    open_cnt += len(items)
    conc_sum += sum(int(x.get("concurrentUserCount") or 0) for x in items)

    return {"openLiveCount": open_cnt, "concurrentUserCount": conc_sum}



def fetch_page(next_params: dict | None = None,
    size: int = 50,
    verbose = True,
    backoff=1.5):
    # next_params 가 dict면 그 키-값을 그대로 쿼리스트링에 펼쳐서 보냄
    params = {"size": size}
    if next_params:
        if not isinstance(next_params, dict):
            next_params = None
        else:
            if verbose:
                print("[fetch_page] merging next params:", next_params)
            params.update(next_params)
    last_err = None
    try:
        r = requests.get(BASE, params=params, headers=HEADERS, timeout=12)
        r.raise_for_status()
        j = r.json()

        if verbose:
            print("[fetch_page] requested URL:", r.url, "->", r.status_code)
            
        content = j.get("content", {})
        items = content.get("data", [])
        # 카테고리 배열
        if not isinstance(items, list):
            raise FetchError(f"items is not a list: {type(items).__name__}")

        next_obj = content.get("page", {}).get("next")         # dict 또는 None
        # 보통 next_obj가 dict면 다음 호출에서 params.update(next_obj)
        
        
        if verbose:
            print(f"[fetch_page] got items={len(items)}, has_next={bool(next_obj)}")
        return items, next_obj
    except Exception as e:
        last_err = e
        print(f"[fetch_page] Error: {e}")
        return [], None

# 여러 페이지를 순회하며 특정 카테고리 ID 목록에 해당하는 카테고리 정보 수집 *Extract 2
def summarize_categories(target_ids,
                         max_pages=20,
                         page_size=30,
                         verbose=True,
                         timeout: float = DEFAULT_TIMEOUT, sleep_range=(1.0, 2.0)):
    
    from .utils import sleep_with_jitter
    target_set = set(target_ids)
    found: dict[str, dict] = {}
    next_params = None
    
    for page in range(max_pages):

        items, next_params = fetch_page(next_params=next_params, size=page_size)


        if verbose:
            print(f"[page {page+1}] items: {len(items)}, next_params: {bool(next_params)}")

        if not items:
            break

        for it in items:
            cid = it.get("categoryId")
            if cid in target_set and cid not in found:
                found[cid] = {
                    "categoryId": cid,
                    "categoryType": it.get("categoryType"),
                    "categoryValue": it.get("categoryValue"),
                    "openLiveCount": int(it.get("openLiveCount", 0)),
                    "concurrentUserCount": int(it.get("concurrentUserCount", 0)),
                    "posterImageUrl": it.get("posterImageUrl")
                }

        # 목표 개수 채우면 조기 종료
        if len(found) == len(target_set):
            if verbose:
                print("All target categories found.")
            break

        if not next_params:
            if verbose:
                print("No more pages. Stop.")
            break

        sleep_with_jitter(*sleep_range)  # 레이트리밋
    missing = [t for t in target_ids if t not in found]
    print("missing category: ",missing)
    return [found[cid] for cid in target_ids if cid in found], missing

def category_streams_url(categoryType: str, categoryId: str):
        return f"https://api.chzzk.naver.com/service/v2/categories/{categoryType}/{categoryId}/lives?"

# 템플릿이 아니면 그대로 검사하고, 200이면 그대로 반환.
def resolve_thumb_url(url_template: str) -> str | None:
    """
    '.../image_{type}.jpg' 형태의 템플릿에서 유효한 실제 이미지 URL을 찾아 반환.
    템플릿이 아니면 그대로 검사하고, 200이면 그대로 반환.
    """
    # 절대 URL 보정(//host, /path 같은 경우를 대비)
    url_template = normalize(url_template)
    if not url_template:
        print("resolve_thumb_url: Warning: empty URL")
        return None
    # 템플릿이 아니면 바로 검사
    if "{type}" not in url_template:
        try:
            r = requests.get(url_template, headers=IMG_HEADERS, timeout=10, stream=True)
            if r.status_code == 200:
                return url_template
        except Exception:
            print(f"resolve_thumb_url 1st : Warning: Failed to fetch {url_template}")
        return url_template

    # 템플릿이면 후보(type × 확장자) 조합으로 탐색
    for t in TYPE_CANDIDATES:
        u = url_template.replace("{type}", t)
        # 확장자가 고정되어 있지 않다면 확장자도 시도
        base, dot, ext = u.rpartition(".")
        for e in [ext] + [x for x in EXT_CANDIDATES if x != ext]:
            cand = f"{base}.{e}"
            try:
                r = requests.get(cand, headers=IMG_HEADERS, timeout=10, stream=True)
                if r.status_code == 200 and int(r.headers.get("Content-Length", "1")) > 100:
                    return cand
            except Exception:
                print(f"resolve_thumb_url 2nd : Warning: Failed to fetch {cand}")
                continue
    return cand


# resolve_thumb_url 실행 후 스트림 데이터에 thumb_url 필드 추가 *Extract 4
def add_thumb_url(stream_data: dict):
    print("Resolving thumbnail URLs...")
    for row in stream_data.values():
        thumb_url_template = row["liveImageUrl"]
        if thumb_url_template:
            resolved = resolve_thumb_url(thumb_url_template)
            if resolved:
                row["thumb_url"] = resolved
            else:
                print(f"Warning: Could not resolve thumb_url")
    return stream_data

def _fetch_top2_for_row(row, size=10, timeout=10):
    base = category_streams_url(row["categoryType"], row["categoryId"])
    params = {"size": size}
    sess = _get_session()
    r = sess.get(base, params=params, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    j = r.json()
    items = (j.get("content") or {}).get("data") or []

    out = []
    for i in range(min(2, len(items))):  # IndexError 방지
        it = items[i]
        ch = (it.get("channel") or {})
        out.append({
            "categoryId": row.get("categoryId"),
            "channelName": ch.get("channelName"),
            "stream_url": f"https://chzzk.naver.com/live/{ch.get('channelId')}",
            "channelId": ch.get("channelId"),
            "channelImageUrl": ch.get("channelImageUrl"),
            "liveImageUrl": it.get("liveImageUrl"),
            "liveTitle": it.get("liveTitle"),
            "concurrentUserCount": it.get("concurrentUserCount"),
            "liveCategoryValue": it.get("liveCategoryValue"),
            "rank": i + 1,
        })
    return out

# 특정 카테고리의 스트림 데이터 수집 *Extract 3
def get_streams_data_parallel(rows: list[dict], start_index: int = 0, max_workers: int = 8) -> dict[int, dict]:

    stream: dict[int, dict] = {}
    base_indices = [start_index + pos * 2 for pos in range(len(rows))]

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        fut2base = {ex.submit(_fetch_top2_for_row, row): base for row, base in zip(rows, base_indices)}
        for fut in as_completed(fut2base):
            base = fut2base[fut]
            try:
                items = fut.result() or []
            except Exception as e:
                # 실패한 카테고리는 스킵 (원하면 로그)
                items = []
            for i, item in enumerate(items):
                stream[base + i] = item

    return stream