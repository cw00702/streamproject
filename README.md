
# streamspot_etl (modularized, with category page support)

## 구조
```
streamspot_etl/
  config.py     # .env 설정, 헤더, API URL
  extract.py    # (A) 카테고리 페이지 수집, (B) 카테고리별 상위 2개 방송 수집
  transform.py  # 썸네일 URL 해상(간단 구현)
  load.py       # Supabase insert/upsert 통합(write_rows) + Cloudinary 업로드
  pipeline.py   # run_full_pipeline: category → streams → DB 적재
  utils.py
```

## 환경 변수(.env)
```env
SUPABASE_URL=...
SUPABASE_KEY=...
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
USER_AGENT=Mozilla/5.0 (chzzk-insights crawler)
HTTP_TIMEOUT=10
PAGE_SIZE=30
```

## 사용 예
```python
from streamspot_etl.pipeline import run_full_pipeline

targets = [
    "Minecraft","Lost_Ark","Player_Unknowns_Battle_Grounds","Black_Survival_Eternal_Return",
    "various_games","Teamfight_Tactics","talk","StarCraft_Remastered","MapleStory","Hearthstone",
    "League_of_Legends","World_of_Warcraft_The_War_Within","Escape_from_Tarkov","OVERWATCH",
    "art","mabinogimobile","Dungeon_Fighter","DEAD_BY_DAYLIGHT","TEKKEN8","Apex_Legends"
]

streams = run_full_pipeline(targets, max_workers=8, upload_thumbs=False)
```

## 메모
- 카테고리 페이지는 `extract.fetch_category_page`/`summarize_categories_by_value`로 순회 수집합니다.
- `upsert_current_top_streams`의 `on_conflict`는 `["categoryId", "rank"]`로 교정되어 있습니다.
- 썸네일 해상/업로드는 선택입니다. 서버 레이트리밋을 고려해 `max_workers`는 점진적으로 늘리세요.

# StreamSpot API (Step 1: Scaffold with mocks)

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn apps.api.main:app --reload --port 8000
```

Open http://localhost:8000/docs

## Endpoints
- `GET /api/categories` — 카테고리 목록(id/label) [mock]
- `GET /api/timeseries?categoryIds=Lost_Ark,Minecraft&step_minutes=30` — 시계열 [mock]
- `GET /api/top-streams?categoryId=Lost_Ark&limit=2` — 현재 상위 스트림 카드 [mock]
- `GET /health`

## Why this structure?
- **Routers 분리**: 기능별 분리(카테고리/시계열/상위스트림)로 유지보수 용이
- **Pydantic 스키마**: 응답 계약(response_model) 명확화 → 프론트 타입/자동 문서화
- **Query params**: GET·멱등성·캐시 친화(프론트의 URL 공유/북마크 용이)
- **Prefix(/api)**: 리버스 프록시나 프런트와의 경로 충돌 방지
- **CORS**: 허용 도메인만 남길 수 있게 `CORS_ALLOW_ORIGINS` 환경 변수로 제어
- **UTC·ISO8601**: 시계열/호버 싱크에서 타임존 오류 방지

## Next step (Step 2)
- Supabase 연결(서버 사이드)로 mock → 실제 데이터로 교체
- `top_streams_history`가 생기면 `at`(시점) 파라미터를 활성화