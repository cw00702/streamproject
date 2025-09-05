
from __future__ import annotations
from typing import Iterable, Iterator
from itertools import islice
import random, time
from urllib.parse import urlparse

def chunked_iter(iterable: Iterable[dict], size: int) -> Iterator[list[dict]]:
    it = iter(iterable)
    while True:
        batch = list(islice(it, size))
        if not batch:
            break
        yield batch

def sleep_with_jitter(a: float = 1.0, b: float = 2.0) -> None:
    time.sleep(random.uniform(a, b))
    
def normalize(u: str) -> str:
    if not u:
        print("normalize: Warning: empty URL")
        return u
    if u.startswith("//"):
        return "https:" + u
    if u.startswith("/"):
        return "https://chzzk.naver.com" + u
    return u

#URL에 스킴(scheme, 예: http, https)이 포함되어 있으면 절대 URL로 보고 True를, 그렇지 않거나 예외가 발생하면 False를 돌려줍니다.
def is_abs_url(u: str| None) -> bool:
    if not u:
        return False
    try:
        return bool(urlparse(u).scheme)
    except Exception:
        return False