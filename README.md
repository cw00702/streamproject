
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


## Endpoints
- `GET /api/categories` — 카테고리 목록(id/label) [mock]
- `GET /api/timeseries?categoryIds=Lost_Ark,Minecraft&step_minutes=30` — 시계열 [mock]
- `GET /api/top-streams?categoryId=Lost_Ark&limit=2` — 현재 상위 스트림 카드 [mock]
- `GET /health`
