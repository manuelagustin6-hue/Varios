#!/usr/bin/env python3
"""Descarga imágenes generadas en ElevenLabs y las guarda como JPG.

Cada línea de la entrada estándar: <destino.jpg> <sesión> <generación> <firma>
"""
import io, subprocess, sys
from PIL import Image

BASE = "https://elevenlabsusercontent.com/database/workspace/e562bf1fcc38415a8b056dd3ddb0a900/content_generation"
for linea in sys.stdin:
    if not linea.strip():
        continue
    destino, sesion, gen, firma = linea.split()
    url = f"{BASE}/{sesion}/{gen}/content.png?Expires=1794420000&KeyName=assets-cdn-key-1&Signature={firma}"
    datos = subprocess.run(["curl", "-sSf", url], capture_output=True, check=True).stdout
    Image.open(io.BytesIO(datos)).convert("RGB").save(destino, quality=90)
    print("ok", destino)
