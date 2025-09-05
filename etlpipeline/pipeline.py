from __future__ import annotations
from datetime import datetime, timezone
import time
from etlpipeline.extract import summarize_categories, get_streams_data_parallel, add_thumb_url, get_streams_data_parallel
from etlpipeline.transform import transform_for_current_top_streams, transform_for_category_totals, add_thumb_url_parallel
from etlpipeline.load import load_category_img, load_stream_thumb_parallel, upsert_category_totals, upsert_current_top_streams
from .config import targets

def run_full_pipeline():
    
    category_crawling = summarize_categories(targets, max_pages=25, page_size=30, verbose=False)# 카테고리 정보 수집
    category_crawling = load_category_img(category_crawling)
    stream_data = get_streams_data_parallel(category_crawling)# 카테고리의 첫 번째 항목(마크)을 대상으로 스트리밍 데이터 수집 stream_data에 top 2개 들어있음
    stream_data = add_thumb_url_parallel(stream_data, 8) # 썸네일 URL 해상해서 이미지 URL 얻어서 stram_data에 추가
    stream_data = load_stream_thumb_parallel(stream_data) # 첫 번째 스트림의 썸네일을 Cloudinary에 업로드하고 secure_url 필드 추가
    print("\n=== Extract END ===")
    #transform
    stream_data = transform_for_current_top_streams(stream_data)
    category_totals = transform_for_category_totals(category_crawling)
    print("\n=== Transform END ===")
    #load to supabase
    upsert_category_totals(category_totals)
    upsert_current_top_streams(stream_data)
    print("\n=== Load END ===")