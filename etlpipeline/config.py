from __future__ import annotations
import os
from dotenv import load_dotenv


env_path = os.path.join(os.getcwd(), "accode.env")
load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

DEFAULT_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "10"))
DEFAULT_PAGE_SIZE = int(os.getenv("PAGE_SIZE", "30"))
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (chzzk-insights crawler)")

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json",
    "Referer": "https://chzzk.naver.com/",
}
BASE = "https://api.chzzk.naver.com/service/v1/categories/live"

targets = [
    "Minecraft","Lost_Ark","Player_Unknowns_Battle_Grounds","Black_Survival_Eternal_Return",
    "various_games","Teamfight_Tactics","talk","StarCraft_Remastered","MapleStory","Hearthstone",
    "League_of_Legends","World_of_Warcraft_The_War_Within","Escape_from_Tarkov","OVERWATCH",
    "art","mabinogimobile","Dungeon_Fighter","DEAD_BY_DAYLIGHT","TEKKEN8","Apex_Legends","music","Genshin_Impact","Hollow_Knight_Silksong","NIKKE_The_Goddess_of_Victory","WutheringWaves","Valorant","AION2","Trickcal","Yu_Gi_Oh_Master_Duel","Honkai_Impact_Star_Rail"
]

targets_map = {
    "Minecraft":"GAME","Lost_Ark":"GAME","Player_Unknowns_Battle_Grounds":"GAME","Black_Survival_Eternal_Return":"GAME",
    "various_games":"GAME","Teamfight_Tactics":"GAME","talk":"ETC","StarCraft_Remastered":"GAME","MapleStory":"GAME","Hearthstone":"GAME",
    "League_of_Legends":"GAME","World_of_Warcraft_The_War_Within":"GAME","Escape_from_Tarkov":"GAME","OVERWATCH":"GAME",
    "art":"ETC","mabinogimobile":"GAME","Dungeon_Fighter":"GAME","DEAD_BY_DAYLIGHT":"GAME","TEKKEN8":"GAME","Apex_Legends":"GAME","music":"ETC","Genshin_Impact":"GAME","Hollow_Knight_Silksong":"GAME","NIKKE_The_Goddess_of_Victory":"GAME","WutheringWaves":"GAME","Valorant":"GAME","AION2":"GAME","Trickcal":"GAME","Yu_Gi_Oh_Master_Duel":"GAME","Honkai_Impact_Star_Rail":"GAME"
}


targets_value_map = {
    "Minecraft":"마인크래프트","Lost_Ark":"로스트아크","Player_Unknowns_Battle_Grounds":"PUBG: 배틀그라운드","Black_Survival_Eternal_Return":"이터널 리턴",
    "various_games":"종합 게임","Teamfight_Tactics":"전략적 팀 전투: K.O. 콜로세움","talk":"talk","StarCraft_Remastered":"스타크래프트 : 리마스터","MapleStory":"메이플스토리","Hearthstone":"하스스톤",
    "League_of_Legends":"리그 오브 레전드","World_of_Warcraft_The_War_Within":"월드 오브 워크래프트: 내부 전쟁","Escape_from_Tarkov":"이스케이프 프롬 타르코프","OVERWATCH":"오버워치 2",
    "art":"그림/아트","mabinogimobile":"마비노기 모바일","Dungeon_Fighter":"던전앤파이터","DEAD_BY_DAYLIGHT":"데드 바이 데이라이트","TEKKEN8":"철권 8","Apex_Legends":"에이펙스 레전드","music":"음악/노래","Genshin_Impact":"GAME","Hollow_Knight_Silksong":"할로우 나이트: 실크송","NIKKE_The_Goddess_of_Victory":"승리의 여신: 니케","WutheringWaves":"명조: 워더링 웨이브","Valorant":"발로란트","AION2":"GAME","Trickcal":"GAME","Yu_Gi_Oh_Master_Duel":"유희왕 마스터 듀얼","Honkai_Impact_Star_Rail":"붕괴: 스타레일"
}


BAD_VALUES = {"", "EMPTY", "NULL", "NONE"}




IMG_HEADERS = {
    "User-Agent": "Mozilla/5.0 (chzzk-insights crawler)",
    "Referer": "https://chzzk.naver.com/",
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
}

TYPE_CANDIDATES = ["360"]     # 필요하면 추가
EXT_CANDIDATES  = ["jpg"]   # 서버가 .jpg만 주면 그대로 갑니다

CATEGORY_STREAMS_BASE = "https://api.chzzk.naver.com/service/v1/categories/live"

def category_streams_url(categoryType: str | int, categoryId: str | int) -> str:
    return CATEGORY_STREAMS_BASE

# Supabase
try:
    from supabase import create_client, Client  # type: ignore
    sb: Client | None = None
    if SUPABASE_URL and SUPABASE_KEY:
        sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    else:
        sb = None
except Exception:
    sb = None
