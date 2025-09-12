from __future__ import annotations
from datetime import datetime, timezone
import time
from etlpipeline.extract import summarize_categories, get_streams_data_parallel, add_thumb_url, get_streams_data_parallel,has_live_for_category, compute_totals_via_v2
from etlpipeline.transform import transform_for_current_top_streams, transform_for_category_totals, add_thumb_url_parallel, transform_for_categories
from etlpipeline.load import upsert_category_totals, upsert_current_top_streams, upsert_categories
from .config import targets, targets_map, targets_value_map
from pprint import pprint

def run_full_pipeline():
    category_rows, missing = summarize_categories(targets, max_pages=20, page_size=30, verbose=False)
    for_stream_data = category_rows
    if missing:
        for cid in missing:
            ctype = targets_map.get(cid)
            try:
                if has_live_for_category(ctype, cid):
                    rows2, miss2 = summarize_categories([cid], max_pages=20, page_size=30, verbose=False)
                    category_rows = rows2
                else:
                    category_rows.append({
                    "categoryId": cid, "categoryType": ctype,
                    "categoryValue": targets_value_map.get(cid), "posterImageUrl": None,
                    "openLiveCount": 0, "concurrentUserCount": 0
                })
            except Exception as e:
                print(f"[fallback] {cid} 보강 실패: {e}")
    
    stream_data = get_streams_data_parallel(for_stream_data)# 카테고리의 첫 번째 항목(마크)을 대상으로 스트리밍 데이터 수집 stream_data에 top 2개 들어있음
    stream_data = add_thumb_url_parallel(stream_data, 8) # 썸네일 URL 해상해서 이미지 URL 얻어서 stram_data에 추가
    print("\n=== Extract END ===")
    #transform
    stream_data = transform_for_current_top_streams(stream_data)
    category_totals = transform_for_category_totals(category_rows)
    categories_data = transform_for_categories(for_stream_data)
    print("\n=== Transform END ===")
    #load to supabase
    upsert_categories(categories_data)
    upsert_category_totals(category_totals)
    upsert_current_top_streams(stream_data)
    print("\n=== Load END ===")