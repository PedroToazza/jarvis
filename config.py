"""
╔══════════════════════════════════════════╗
║          JARVIS — config.py              ║
╚══════════════════════════════════════════╝
"""
import os
import sys
from pathlib import Path

def resource_path(relative):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative)


def _project_dir():
    if hasattr(sys, 'frozen') and sys.frozen:
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def _load_local_env():
    env_path = _project_dir() / '.env'
    if not env_path.is_file():
        return

    try:
        for raw_line in env_path.read_text(encoding='utf-8').splitlines():
            line = raw_line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value and key not in os.environ:
                os.environ[key] = value
    except OSError:
        pass


def _env(*names, default=''):
    for name in names:
        value = os.getenv(name, '').strip()
        if value:
            return value
    return default


_load_local_env()

# ─── VOZ ──────────────────────────────────────────────────────────────
WAKE_WORD       = "jarvis"
COMMAND_TIMEOUT = 8

# ─── PALMAS ───────────────────────────────────────────────────────────
CLAP_PEAK_THRESHOLD    = 0.06
CLAP_SUSTAIN_THRESHOLD = 0.012
CLAP_MAX_INTERVAL      = 0.9
CLAP_COOLDOWN          = 2.5

# ─── SPOTIFY ──────────────────────────────────────────────────────────
SPOTIFY_CLIENT_ID     = _env('SPOTIFY_CLIENT_ID', 'spotify_client_id')
SPOTIFY_CLIENT_SECRET = _env('SPOTIFY_CLIENT_SECRET', 'spotify_client_secret')
SPOTIFY_REDIRECT_URI  = _env('SPOTIFY_REDIRECT_URI', default='http://127.0.0.1:8888/callback')
SPOTIFY_SCOPE         = (
    "user-modify-playback-state "
    "user-read-playback-state "
    "playlist-read-private "
    "playlist-read-collaborative"
)

# ─── TTS Microsoft Edge ──────────────────────────────────────────────
# Vozes pt-BR:
#   pt-BR-AntonioNeural              ← padrão
#   pt-BR-MacerioMultilingualNeural  ← mais natural
#   pt-BR-FranciscaNeural            ← feminina
#   pt-BR-ThalitaMultilingualNeural  ← feminina mais jovem
TTS_VOICE  = "pt-BR-AntonioNeural"
TTS_RATE   = 165
TTS_VOLUME = 0.9

# ─── IA (Gemini 1.5 Flash) ───────────────────────────────────────────
# Grátis 1500 req/dia: https://aistudio.google.com/apikey
GEMINI_API_KEY = _env('GEMINI_API_KEY', 'gemini')