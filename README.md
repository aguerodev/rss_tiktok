# Generador de RSS para TikTok

Genera feeds RSS a partir de cuentas de usuarios de TikTok.

## Configuración Rápida

### GitHub Actions (Recomendado)

1. Haz un fork de este repositorio
2. Habilita GitHub Actions en la pestaña Actions
3. Habilita GitHub Pages
4. Obtén tu `ms_token` de TikTok:
   - Inicia sesión en TikTok desde Chrome en escritorio
   - Abre DevTools (F12) > Application > Cookies > https://www.tiktok.com
   - Copia el valor de `msToken`
5. Añade el token a los secretos del repositorio:
   - Ve a Settings > Secrets and Variables > Actions
   - Crea un nuevo secreto:
     - Nombre: `MS_TOKEN`
     - Valor: Tu valor de msToken
6. Edita los nombres de usuario en `subscriptions.csv`
7. Actualiza `config.py` con tu URL de GitHub Pages

El workflow se ejecutará cada 4 horas y generará archivos RSS en el directorio `rss`.

### Ejecución Local

```bash
# Configuración
pip install virtualenv
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configurar token
export MS_TOKEN="tu_token_aquí"  # En Windows: set MS_TOKEN=tu_token_aquí

# Ejecutar
python postprocessing.py
```

## URLs de los Feeds RSS

Accede a tus feeds en: `https://tu-usuario.github.io/rss_tiktok/rss/nombreusuario.xml`