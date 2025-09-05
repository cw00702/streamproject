from __future__ import annotations
from .config import cloudinary
from typing import Iterable, Sequence, Literal
from concurrent.futures import ThreadPoolExecutor, as_completed
import cloudinary.uploader
from .utils import chunked_iter
from .config import sb

# 특정 카테고리의 대표 이미지(포스터)를 Cloudinary에 업로드 후 secure_url 필드에 추가
def load_category_img(result: list[dict]):
    # 원격 이미지 URL을 Cloudinary에 업로드
    
    for row in result:
        if not row.get("posterImageUrl"):
            print(f"Cloudinary 업로드 생략: posterImageUrl 없음 ({row} ,{row.get('categoryId')})")
            continue
        try:
            url = row.get("posterImageUrl")
            
            upload_result = cloudinary.uploader.upload(
                url,
                public_id=f"chzzimg/{row.get("categoryId")}",   # 저장할 경로/이름
                overwrite=True,                     # 매번 덮어쓰기
                invalidate=True                     # 캐시 무효화
            )
            row["secure_url"] = upload_result["secure_url"]
        except Exception as e:
            print(f"Cloudinary 업로드 실패: {e} ({row.get('categoryId')})")
            continue
    return result  # 업로드된 Cloudinary 이미지 주소 포함 반환

# 특정 스트림의 썸네일 이미지를 Cloudinary에 업로드 후 secure_url 필드에 추가
def load_stream_thumb(stream_data: dict):
    # 원격 이미지 URL을 Cloudinary에 업로드
    
    for row in stream_data.values():
        url = row.get("thumb_url")
        if not url:
            print(f"Cloudinary 업로드 생략: thumb_url 없음 ({row} ,{row.get('categoryId')}, {row.get('rank')})")
            continue
        try:
            upload_result = cloudinary.uploader.upload(
                url, 
                public_id=f"chzzthumb/{row["categoryId"]}/rank_{row["rank"]}",   # 저장할 경로/이름
                overwrite=True,                     # 매번 덮어쓰기
                invalidate=True                     # 캐시 무효화
            )
            row["secure_url"] = upload_result["secure_url"]
        except Exception as e:
            print(f"Cloudinary 업로드 실패: {e} ({row.get('categoryId')}, {row.get('rank')})")
            continue
    return stream_data  # 업로드된 Cloudinary 이미지 주소 포함 반환

def chunked(lst, n=1000):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def upsert_categories(rows: list[dict]):
    # on_conflict는 category_id
    try:
        for batch in chunked(rows, 500):
            sb.table("categories") \
            .upsert(batch, on_conflict="id") \
            .execute()
    except Exception as e:
        print(f"Error during upsert_categories: {e}")
        
def upsert_current_top_streams(rows: list[dict]):
    # on_conflict는 (category_id, rank)
    try:
        for batch in chunked(rows, 500):
            sb.table("current_top_streams") \
            .upsert(batch, on_conflict=["categoryId,rank"]) \
            .execute()
        print("Upserted current_top_streams.")
    except Exception as e:
        print(f"Error during upsert_current_top_streams: {e}")
        
def upsert_category_totals(rows: list[dict]):
    # on_conflict는 category_id
    try:
        for batch in chunked(rows, 500):
            sb.table("category_totals") \
            .insert(batch) \
            .execute()
        print("Inserted category_totals.")
    except Exception as e:
        print(f"Error during category_totals: {e}")
        
def load_stream_thumb_parallel(stream_data: dict[int, dict], workers: int = 4) -> dict[int, dict]:
    keys = [k for k, v in stream_data.items() if v.get("thumb_url")]

    def _upload(k: int):
        row = stream_data[k]
        try:
            r = cloudinary.uploader.upload(
                row["thumb_url"],
                public_id=f"chzzthumb/{row['categoryId']}/rank_{row['rank']}",
                overwrite=True,
                invalidate=True,
            )
            return (k, r.get("secure_url"))
        except Exception:
            return (k, None)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(_upload, k) for k in keys]
        for fut in as_completed(futs):
            k, surl = fut.result()
            if surl:
                stream_data[k]["secure_url"] = surl
    return stream_data