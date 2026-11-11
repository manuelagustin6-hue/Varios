# Producción de videos

Cada carpeta `NNN/` contiene un Short terminado y todo lo necesario para regenerarlo.

| Archivo | Contenido |
|---|---|
| `video.mp4` | **Video final** listo para publicar (1080×1920, 30 fps, ~40 s, audio normalizado a −14 LUFS). |
| `config.json` | Qué imagen va en cada momento, títulos destacados y reemplazos de números en los subtítulos. |
| `palabras.json` | Transcripción de la voz con el tiempo de cada palabra (ElevenLabs Scribe). |
| `subtitulos.ass` | Subtítulos generados (se queman en el video). |
| `img/` | Imágenes de fondo generadas con IA (sin personas reales ni logos de marcas). |

## Regenerar un video

```bash
python3 herramientas/render.py produccion/001
```

## Estado

| # | Video | Duración |
|---|---|---|
| 001 | Blockbuster y Netflix | 41,7 s |
| 002 | Kodak y la cámara digital | 42,0 s |
| 003 | La pizza de los 10.000 bitcoins | 39,6 s |
| 004 | El Post-it | 41,7 s |
| 005 | Ronald Wayne y Apple | 42,7 s |
| 006 | El hombre que vendió la Torre Eiffel | 44,5 s |
| 007 | El logo de Nike | 41,4 s |
| 008 | Google.com por 12 dólares | 41,6 s |
| 009 | Red Bull y las latas en la basura | 40,2 s |
| 010 | M&M's rechazó aparecer en E.T. | 48,2 s |
| 011 | Kearns contra Ford y Chrysler | 47,2 s |
| 012 | El recorrido de IKEA | 42,7 s |
| 013 | Adidas dejó ir a Michael Jordan | 41,5 s |

## Al publicar

- **Título, texto y hashtags:** listos para copiar en `publicacion.md`.
- **Música:** los videos no llevan música para evitar reclamos de derechos. Agregala al subir, desde la biblioteca de cada plataforma, con volumen bajo (10–15 %).
- **Etiqueta de contenido con IA:** las imágenes son realistas y generadas con IA. Marcá la opción correspondiente al subir: en YouTube, «Contenido alterado o sintético»; en TikTok, «Contenido generado por IA»; en Instagram, «Etiqueta de IA». Es un requisito de las plataformas y evita sanciones.
- **Portada:** elegí como portada el primer fotograma (el que tiene el título amarillo).
