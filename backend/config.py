import os
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Optional
from dotenv import load_dotenv

# Directorio raíz del proyecto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

# Cargar variables de entorno desde .env
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Forzar zona horaria a nivel de sistema operativo en Linux/Render
try:
    os.environ['TZ'] = 'America/Merida'
    if hasattr(time, 'tzset'):
        time.tzset()
except Exception:
    pass

# Forzar salida en UTF-8 para consola en Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Zona horaria oficial de Mérida, Yucatán (UTC-6 todo el año sin horario de verano)
TZ_MERIDA = timezone(timedelta(hours=-6))

def ahora_merida() -> datetime:
    """Retorna la fecha y hora actual en la zona horaria de Mérida, Yucatán (UTC-6)."""
    return datetime.now(timezone.utc).astimezone(TZ_MERIDA)

def fecha_hoy_merida() -> str:
    """Retorna la fecha actual en Mérida en formato YYYY-MM-DD."""
    return ahora_merida().strftime("%Y-%m-%d")

def format_merida_dt(dt: Optional[datetime]) -> Optional[str]:
    """
    Convierte un datetime (UTC o naive) a string 'YYYY-MM-DD HH:MM:SS'
    en la hora local oficial de Mérida, Yucatán (UTC-6).
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(TZ_MERIDA).strftime("%Y-%m-%d %H:%M:%S")

def format_merida_time(dt: Optional[datetime]) -> Optional[str]:
    """Retorna la hora 'HH:MM:SS' en horario de Mérida, Yucatán (UTC-6)."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(TZ_MERIDA).strftime("%H:%M:%S")

PORT = int(os.getenv("PORT", 5000))
CRON_SECRET = os.getenv("CRON_SECRET", "lex_cron_2026_secreto").strip().strip('"').strip("'")
