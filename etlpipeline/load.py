from __future__ import annotations
from typing import Iterable, Sequence, Literal
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import chunked_iter
from .config import sb


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