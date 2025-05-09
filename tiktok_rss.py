#!/usr/bin/env python3
"""
TikTok RSS - Generador ultra-optimizado de feeds RSS para TikTok
Sin capturas de thumbnails, sin imágenes, solo texto puro y enlaces.

Diseñado para usar con uv.lock para gestión de dependencias.
"""

import os
import asyncio
import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from feedgen.feed import FeedGenerator
from TikTokApi import TikTokApi

# Constantes
RSS_DIR = Path("rss")
MAX_VIDEOS = 10
MAX_TEXT_LENGTH = 255
BASE_URL = os.environ.get("RSS_BASE_URL", "https://raw.githubusercontent.com/usuario/tiktok-rss/main/v3/")

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("tiktok-rss")

# Garantizar que el directorio de salida exista
RSS_DIR.mkdir(exist_ok=True)

async def generate_feed(username: str, api_instance: TikTokApi) -> None:
    """Genera un feed RSS para un usuario específico de TikTok."""
    logger.info(f"Generando feed para: {username}")
    
    # Configurar el generador de feed
    fg = FeedGenerator()
    fg.id(f"https://www.tiktok.com/@{username}")
    fg.title(f"{username} TikTok")
    fg.link(href="https://tiktok.com", rel="alternate")
    fg.subtitle(f"Últimos TikToks de {username}")
    fg.link(href=f"{BASE_URL}rss/{username}.xml", rel="self")
    fg.language("es")
    
    # Inicializar usuario de TikTok
    try:
        ttuser = api_instance.user(username)
        user_data = await ttuser.info()
        
        # Timestamp más reciente para actualización del feed
        latest_update = None
        
        # Procesar videos
        async for video in ttuser.videos(count=MAX_VIDEOS):
            entry = fg.add_entry()
            
            # Datos básicos
            video_id = video.id
            video_data = video.as_dict
            video_url = f"https://tiktok.com/@{username}/video/{video_id}"
            
            # Timestamp
            create_time = datetime.fromtimestamp(video_data['createTime'], timezone.utc)
            latest_update = max(create_time, latest_update) if latest_update else create_time
            
            # Contenido
            description = video_data.get('desc', '')
            title = description[:MAX_TEXT_LENGTH] if description else f"Video de {username}"
            
            # Configurar entrada
            entry.id(video_url)
            entry.title(title)
            entry.link(href=video_url)
            entry.published(create_time)
            entry.updated(create_time)
            
            # Contenido en texto plano con enlace directo al video
            content = f"{description[:MAX_TEXT_LENGTH] if description else 'Sin descripción'}\n\n"
            content += f"Ver en TikTok: {video_url}"
            
            # Añadir estadísticas si están disponibles
            stats = video_data.get('stats', {})
            if stats:
                content += f"\n\n👍 {stats.get('diggCount', 0)} | "
                content += f"💬 {stats.get('commentCount', 0)} | "
                content += f"🔄 {stats.get('shareCount', 0)}"
            
            entry.content(content, type="text")
        
        # Actualizar timestamp del feed
        if latest_update:
            fg.updated(latest_update)
        
        # Guardar feed
        output_file = RSS_DIR / f"{username}.xml"
        fg.rss_file(output_file, pretty=True)
        logger.info(f"Feed generado exitosamente: {output_file}")
        
    except Exception as e:
        logger.error(f"Error generando feed para {username}: {e}")

async def main() -> None:
    """Función principal para generar feeds RSS."""
    # Verificar token de autenticación
    ms_token = os.environ.get("MS_TOKEN")
    if not ms_token:
        logger.error("Variable de entorno MS_TOKEN no definida")
        return
    
    # Leer usuarios desde CSV
    usernames = []
    try:
        with open("subscriptions.csv") as f:
            reader = csv.DictReader(f, fieldnames=["username"])
            for row in reader:
                username = row["username"].strip().rstrip(",")
                if username:
                    usernames.append(username)
    except Exception as e:
        logger.error(f"Error leyendo subscriptions.csv: {e}")
        return
    
    if not usernames:
        logger.warning("No se encontraron usuarios en subscriptions.csv")
        return
    
    logger.info(f"Procesando {len(usernames)} usuarios")
    
    # Inicializar API de TikTok
    try:
        async with TikTokApi() as api:
            await api.create_sessions(
                ms_tokens=[ms_token],
                num_sessions=1,
                sleep_after=1,
                headless=True  # Modo headless para mayor rapidez
            )
            
            # Procesar usuarios en secuencia
            for username in usernames:
                await generate_feed(username, api)
    except Exception as e:
        logger.error(f"Error general de la API de TikTok: {e}")
    
    logger.info("Proceso de generación de feeds completado")

if __name__ == "__main__":
    asyncio.run(main())