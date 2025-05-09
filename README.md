# TikTok RSS Ultra

Generador ultra-optimizado de feeds RSS para TikTok.

## Características

- **Minimalista:** Un solo archivo Python
- **Rápido:** Sin capturas de pantalla ni imágenes
- **Simple:** Feeds RSS textuales con enlaces directos

## Uso rápido

```bash
# Método 1: Con pip
pip install TikTokApi feedgen
python run.py "tu_token_aquí"

# Método 2: Usando la variable de entorno
export MS_TOKEN="tu_token_aquí"
python tiktok_rss.py
```

## Configuración

Edita `subscriptions.csv` para añadir usuarios de TikTok a seguir.

## Obtener el token de TikTok

1. Inicia sesión en TikTok desde Chrome
2. Abre DevTools con F12
3. Ve a Application > Storage > Cookies > https://www.tiktok.com
4. Copia el valor de la cookie `msToken`

## Estructura del proyecto

- `tiktok_rss.py`: Script principal
- `run.py`: Helper para ejecutar fácilmente con token
- `subscriptions.csv`: Lista de usuarios
- `requirements.txt`: Dependencias mínimas
- `rss/`: Feeds RSS generados

## GitHub Actions

El proyecto está configurado para ejecutarse automáticamente cada 4 horas utilizando GitHub Actions, generando feeds RSS para todos los usuarios en `subscriptions.csv`.