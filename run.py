#!/usr/bin/env python3
"""
Script auxiliar para ejecutar el generador de RSS con un token desde la línea de comandos
"""

import os
import sys
import asyncio
from tiktok_rss import main

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Leer token de la línea de comandos
        os.environ["MS_TOKEN"] = sys.argv[1]
    
    # Verificar si el token está definido
    if not os.environ.get("MS_TOKEN"):
        print("Error: MS_TOKEN no está definido")
        print("Uso: python run.py <token>")
        print("  o: MS_TOKEN=<token> python run.py")
        sys.exit(1)
    
    # Ejecutar el generador
    asyncio.run(main())