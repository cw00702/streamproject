
# streamspot_etl (modularized, with category page support)
## 기능
'''
스트리밍 사이트의 데이터를 스크래핑하여 데이터 분석 후에 시각화를 진행
'''



## 구조
```
streamspot_etl/
  config.py     # .env 설정, 헤더, API URL
  extract.py    # (A) 카테고리 페이지 수집, (B) 카테고리별 상위 2개 방송 수집 ,썸네일 URL 해상(간단 구현)
  transform.py  # 
  load.py       # Supabase insert/upsert 통합(write_rows)
  pipeline.py   # run_full_pipeline: category → streams → DB 적재
  utils.py
```

## 환경 변수(.env)
```env
SUPABASE_URL=...
SUPABASE_KEY=...
USER_AGENT=Mozilla/5.0 (chzzk-insights crawler)
HTTP_TIMEOUT=10
PAGE_SIZE=30
GitHub Action -> 5분마다 실행
```

targets = [
    "Minecraft","Lost_Ark","Player_Unknowns_Battle_Grounds","Black_Survival_Eternal_Return",
    "various_games","Teamfight_Tactics","talk","StarCraft_Remastered","MapleStory","Hearthstone",
    "League_of_Legends","World_of_Warcraft_The_War_Within","Escape_from_Tarkov","OVERWATCH",
    "art","mabinogimobile","Dungeon_Fighter","DEAD_BY_DAYLIGHT","TEKKEN8","Apex_Legends"
] 이후에 추가

streams = run_full_pipeline(targets, max_workers=8, upload_thumbs=False)
```

## 메모
- 카테고리 페이지는 `extract.fetch_category_page`/`summarize_categories_by_value`로 순회 수집합니다.


## Endpoints
- `GET /api/categories` — 카테고리 목록(id/label) [mock]

