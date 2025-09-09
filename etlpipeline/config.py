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
    "art","mabinogimobile","Dungeon_Fighter","DEAD_BY_DAYLIGHT","TEKKEN8","Apex_Legends"
]

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
