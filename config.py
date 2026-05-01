import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CRICKET_API_KEY = os.getenv("CRICKET_API_KEY")
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"

CACHE_TTL = 60          # seconds
MAX_OVERS_T20 = 20
TOTAL_WICKETS = 10
GEMINI_MODEL = "gemini-2.0-flash"

CRICKET_API_BASE = "https://api.cricapi.com/v1"

# User modes
MODE_ANALYST  = "ANALYST"
MODE_BEGINNER = "BEGINNER"
MODE_MEME     = "MEME"
MODE_STRATEGY = "STRATEGY"

DEFAULT_MODE = MODE_ANALYST

# PitchSense additions
VOICE_LANGUAGE = "en"
VOICE_TLD = "co.in"          # Indian English accent for gTTS
SFX_ENABLED = True
AUTOREFRESH_INTERVAL_MS = 90_000   # 90s auto-refresh
