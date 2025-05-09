#!/usr/bin/env python3
"""
TikTok RSS – versión robusta
────────────────────────────
• Cambios clave
  1. Soporta variables de entorno para `HEADLESS`, `BROWSER` y `MOBILE`.
  2. Reintenta cada usuario hasta 3 veces (con espera exponencial) antes de rendirse.
  3. Opcional: uso de proxy si defines `TIKTOK_PROXY`.
  4. Sigue generando aunque algún usuario falle.
"""

import os
import asyncio
import csv
import logging
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

from feedgen.feed import FeedGenerator
from TikTokApi import TikTokApi

# ──────────────────── Configuración general ────────────────────
RSS_DIR = Path("rss")
RSS_DIR.mkdir(exist_ok=True)

MAX_VIDEOS = int(os.getenv("MAX_VIDEOS", 10))
MAX_TEXT_LENGTH = 255
BASE_URL = os.getenv(
    "RSS_BASE_URL",
    "https://raw.githubusercontent.com/usuario/tiktok-rss/main/v3/",
)

# Opciones de navegador
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
BROWSER = os.getenv("BROWSER", "webkit")        # chromium | firefox | webkit
MOBILE = os.getenv("MOBILE", "true").lower() == "true"

PROXY = os.getenv("TIKTOK_PROXY")  # ej. http://user:pass@host:port

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("tiktok-rss")


# ──────────────────── Funciones auxiliares ────────────────────
async def generate_feed(username: str, api: TikTokApi) -> None:
    """Genera el feed RSS de un usuario TikTok. Retira `headless` para reducir bloqueos."""
    fg = FeedGenerator()
    fg.id(f"https://www.tiktok.com/@{username}")
    fg.title(f"{username} TikTok")
    fg.link(href="https://tiktok.com", rel="alternate")
    fg.subtitle(f"Últimos TikToks de {username}")
    fg.link(href=f"{BASE_URL}rss/{username}.xml", rel="self")
    fg.language("es")

    latest_update: Optional[datetime] = None

    ttuser = api.user(username)
    async for video in ttuser.videos(count=MAX_VIDEOS):
        data = video.as_dict
        vid_url = f"https://tiktok.com/@{username}/video/{video.id}"

        ts = datetime.fromtimestamp(data["createTime"], timezone.utc)
        latest_update = max(latest_update, ts) if latest_update else ts

        desc = (data.get("desc") or "").strip()
        title = desc[:MAX_TEXT_LENGTH] or f"Video de {username}"

        entry = fg.add_entry()
        entry.id(vid_url)
        entry.title(title)
        entry.link(href=vid_url)
        entry.published(ts)
        entry.updated(ts)

        stats = data.get("stats", {})
        content = f"{desc[:MAX_TEXT_LENGTH] or 'Sin descripción'}\n\nVer en TikTok: {vid_url}"
        if stats:
            content += (
                f"\n\n👍 {stats.get('diggCount', 0)} | "
                f"💬 {stats.get('commentCount', 0)} | "
                f"🔄 {stats.get('shareCount', 0)}"
            )
        entry.content(content, type="text")

    if latest_update:
        fg.updated(latest_update)

    out = RSS_DIR / f"{username}.xml"
    fg.rss_file(out, pretty=True)
    log.info(f"✓ Feed guardado: {out}")


async def process_user(username: str, api: TikTokApi, attempts: int = 3) -> None:
    """Intenta generar el feed con reintentos exponenciales."""
    for i in range(1, attempts + 1):
        try:
            await generate_feed(username, api)
            return
        except Exception as e:
            wait = 2 ** i + random.uniform(0, 1)
            log.warning(f"{username}: intento {i}/{attempts} falló → {e} (esperando {wait:.1f}s)")
            await asyncio.sleep(wait)
    log.error(f"✗ No se pudo generar el feed para {username} tras {attempts} intentos")


# ──────────────────── Programa principal ────────────────────
async def main() -> None:
    token = os.getenv("MS_TOKEN")
    if not token:
        log.error("Variable de entorno MS_TOKEN no definida")
        return

    # Cargar lista de usuarios
    try:
        with open("subscriptions.csv") as f:
            usernames = [row["username"].strip() for row in csv.DictReader(f, fieldnames=["username"]) if row["username"].strip()]
    except Exception as e:
        log.error(f"Error leyendo subscriptions.csv: {e}")
        return

    if not usernames:
        log.warning("No hay usuarios en subscriptions.csv")
        return

    log.info(f"Procesando {len(usernames)} usuarios → {', '.join(usernames)}")

    try:
        async with TikTokApi() as api:
            await api.create_sessions(
                ms_tokens=[token],
                num_sessions=1,
                sleep_after=1,
                headless=HEADLESS,
                browser_type=BROWSER,   # ← aquí
                proxy=PROXY,
            )

            for u in usernames:
                await process_user(u, api)
                # Pequeña pausa entre usuarios para reducir detección
                await asyncio.sleep(3)
    except Exception as e:
        log.error(f"Fallo global de TikTokApi: {e}")

    log.info("✓ Generación de feeds terminada")


if __name__ == "__main__":
    asyncio.run(main())
