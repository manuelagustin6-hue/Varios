# Flujo de producción con voz por IA

Objetivo: producir **7 videos por semana** en ~12–15 horas, trabajando por lotes.

## División del trabajo

| Tarea | Responsable |
|---|---|
| Investigación, verificación de datos y guion | Claude (en este repositorio) |
| Títulos, textos y hashtags | Claude |
| Generar la voz con ElevenLabs (2 tomas por guion, en `audios/NNN/`) | Claude |
| Elegir la toma, editar y publicar | Vos |
| Análisis de métricas y ajustes | Claude, con los datos que compartas |

## Semana tipo

| Día | Tarea | Tiempo estimado |
|---|---|---|
| Lunes | Revisar y aprobar los 7 guiones de la semana | 1 h |
| Martes | Buscar el material visual (las voces ya están generadas) | 2–3 h |
| Miércoles y jueves | Editar los 7 videos | 6–8 h |
| Viernes | Miniaturas, programación de publicaciones | 1–2 h |
| Diario | Responder comentarios | 15 min |

## Paso a paso por video

### 1. Voz (la genera Claude)
- **Voz del canal:** «BRIAN – Voz para redes sociales», de ElevenLabs (ID `U9TSK9KHMlMU2qkeXlQP`). Usarla siempre.
- Voz alternativa probada: «Carlos – Español Neutro» (ID `Y4HwpMNrBWN5dFKi5Lw8`), más pausada.
- **Modelo:** Eleven v4.
- Claude genera 2 tomas por guion y las guarda en `audios/NNN/toma-1.mp3` y `toma-2.mp3`. Vos elegís una y queda como `voz-final.mp3`.
- **Costo de referencia:** ~714 créditos por toma de un guion de ~45 s (≈ US$ 0,14 según lo informado por ElevenLabs). Con Brian, el guion 001 dura 41,6 s.
- Para controlar el ritmo, el texto se escribe con puntos suspensivos (…) en las pausas dramáticas y con los números en letras.
- Si la locución supera los 50 s, acelerarla un 5–10 % en la edición.

### 2. Material visual (20 min)
- Fuentes libres: Pexels, Pixabay, Wikimedia Commons (revisar la licencia de cada imagen).
- Para logos y marcas: uso informativo, sin sugerir patrocinio ni relación con la marca.
- Evitar fragmentos de películas, series y noticieros.

### 3. Edición en CapCut (40–60 min)
1. Proyecto 9:16, 1080 × 1920, 30 fps.
2. Importar la voz y cortar silencios largos.
3. Colocar el texto del gancho desde el primer fotograma.
4. Poner material visual sobre la voz con un cambio cada 1,5–3 s; usar zoom suave en imágenes fijas.
5. Subtítulos automáticos → corregir errores → estilo fijo del canal (misma tipografía y colores siempre).
6. Música de la biblioteca con licencia, muy baja respecto de la voz.
7. Efectos de sonido puntuales en los datos clave (golpe, *whoosh*, caja registradora).
8. Último plano conectado con el primero para generar el bucle.
9. Exportar en 1080p sin marca de agua.

### 4. Control de calidad (5 min)
- [ ] ¿El gancho se entiende sin sonido (por el texto en pantalla)?
- [ ] ¿Los subtítulos no tienen errores?
- [ ] ¿Los datos coinciden con las fuentes verificadas?
- [ ] ¿Dura menos de 50 segundos?
- [ ] ¿La música tiene licencia?

### 5. Publicación
- YouTube: título con el dato principal + emoji; agregar el video a la lista de reproducción de su serie.
- TikTok e Instagram: mismo texto, hashtags adaptados.
- Al subir a YouTube, si el video incluye **escenas realistas generadas por IA**, marcar la opción de contenido alterado o sintético. Una voz en off de IA, por sí sola, normalmente no lo requiere (verificar la política vigente).
