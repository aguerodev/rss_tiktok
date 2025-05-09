#!/usr/bin/env python3
"""
TikTok RSS – versión corregida para TikTokApi 7.x
"""

import os
import asyncio
import csv
import random
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from feedgen.feed import FeedGenerator
from TikTokApi import TikTokApi

# ────────────── Config ──────────────
RSS_DIR = Path("rss"); RSS_DIR.mkdir(exist_ok=True)
MAX_VIDEOS = int(os.getenv("MAX_VIDEOS", 10))
BASE_URL   = os.getenv("RSS_BASE_URL", "https://raw.githubusercontent.com/usuario/tiktok-rss/main/v3/")

HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
BROWSER  = os.getenv("BROWSER",  "webkit")      # chromium | firefox | webkit
PROXY    = os.getenv("TIKTOK_PROXY")            # opcional

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S")
log = logging.getLogger("tiktok-rss")

# ────────── Feed generator ──────────
async def generate_feed(user: str, api: TikTokApi) -> None:
    fg = FeedGenerator()
    fg.id(f"https://www.tiktok.com/@{user}")
    fg.title(f"{user} TikTok")
    fg.link(href="https://tiktok.com", rel="alternate")
    fg.subtitle(f"Últimos TikToks de {user}")
    fg.link(href=f"{BASE_URL}rss/{user}.xml", rel="self")
    fg.language("es")

    latest: Optional[datetime] = None
    ttuser = api.user(user)

    async for vid in ttuser.videos(count=MAX_VIDEOS):
        data = vid.as_dict
        url  = f"https://tiktok.com/@{user}/video/{vid.id}"

        ts = datetime.fromtimestamp(data["createTime"], timezone.utc)
        latest = max(latest, ts) if latest else ts

        desc  = (data.get("desc") or "").strip()
        title = desc[:255] or f"Video de {user}"

        entry = fg.add_entry()
        entry.id(url); entry.title(title); entry.link(href=url)
        entry.published(ts); entry.updated(ts)

        stats = data.get("stats", {})
        content = f"{desc[:255] or 'Sin descripción'}\n\nVer en TikTok: {url}"
        if stats:
            content += (
                f"\n\n👍 {stats.get('diggCount', 0)} | "
                f"💬 {stats.get('commentCount', 0)} | "
                f"🔄 {stats.get('shareCount', 0)}"
            )
        entry.content(content, type="text")

    if latest:
        fg.updated(latest)

    out = RSS_DIR / f"{user}.xml"
    fg.rss_file(out, pretty=True)
    log.info(f"✓ Feed guardado: {out}")

# ──────────── Main logic ────────────
async def main() -> None:
    token = os.getenv("MS_TOKEN")
    if not token:
        log.error("MS_TOKEN no definido"); return

    try:
        with open("subscriptions.csv") as f:
            users = [r["username"].strip() for r in csv.DictReader(f, fieldnames=["username"]) if r["username"].strip()]
    except Exception as e:
        log.error(f"Error leyendo CSV: {e}"); return

    if not users:
        log.warning("CSV vacío"); return

    log.info(f"Procesando {len(users)} usuarios → {', '.join(users)}")

    try:
        async with TikTokApi() as api:
            await api.create_sessions(
                ms_tokens=[token],
                num_sessions=1,
                sleep_after=1,
                headless=HEADLESS,
                browser_type=BROWSER,   # ← parámetro correcto
                proxy=PROXY,
            )

            for u in users:
                try:
                    await generate_feed(u, api)
                    await asyncio.sleep(3)
                except Exception as e:
                    log.error(f"{u}: {e}")
    except Exception as e:
        log.error(f"Fallo global de TikTokApi: {e}")

if __name__ == "__main__":
    asyncio.run(main())
