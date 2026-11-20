# L01 — ¿Qué es la TIR? (video largo, horizontal)

- **Formato:** 1920x1080, animado con código (`herramientas/largo.py`).
- **Duración:** unos 5 minutos (702 palabras).
- **Carpeta de producción:** `largos/L01-tir/` (`largo.json` tiene las escenas y las frases).
- **Público:** hispanohablante general, de cualquier país: ejemplos en dólares, sin instrumentos ni normas locales, y con el término en inglés (IRR).
- **Carácter:** educativo. No es una recomendación de inversión (se dice en el video y va en la descripción).

## Cómo grabar la voz

1. Abre `largos/L01-tir/video-guia.mp4` en la computadora y graba con el celular (nota de voz) cerca de la boca, en un lugar sin eco.
2. Después de la cuenta regresiva (3, 2, 1), lee la frase de la banda inferior siguiendo el resaltado dorado. El ritmo es tranquilo: 2,5 palabras por segundo.
3. Graba todo de corrido. Si te equivocas, sigue: la toma no tiene que ser perfecta.
4. Envía el audio (mp3, m4a o wav). Se une al video limpio con:
   `python3 herramientas/largo.py largos/L01-tir limpio voz.mp3`

Si tu ritmo natural es distinto, se ajustan los tiempos de las escenas a tu audio en lugar de que tú sigas al video.

## Guion

**1. Gancho**
Dos inversiones te prometen exactamente la misma ganancia: quinientos dólares. Pero una es casi seis veces mejor que la otra. Y la forma de saberlo tiene solo tres letras: TIR.

**2. Dos inversiones**
Mira estas dos opciones. En la inversión A pones mil dólares hoy y dentro de un año recibes mil quinientos. En la inversión B también pones mil dólares y también recibes mil quinientos... pero dentro de cinco años. Las dos ganan quinientos dólares. Entonces, ¿son iguales? No. Porque en la A recuperas tu dinero cuatro años antes, y en ese tiempo puedes volver a invertirlo.

**3. El valor del dinero en el tiempo**
Esta es la idea más importante de las finanzas: el dinero vale distinto según cuándo lo recibes. Cien dólares hoy valen más que cien dólares dentro de un año, porque los de hoy los puedes poner a trabajar. Por eso, para comparar inversiones no alcanza con mirar cuánto ganas. Hay que mirar cuánto ganas por año.

**4. Definición**
Y eso es lo que mide la TIR, la tasa interna de retorno. En inglés la verás como IRR, internal rate of return: es exactamente lo mismo. Es el rendimiento anual de una inversión, teniendo en cuenta todo lo que pones, todo lo que recibes y, sobre todo, cuándo. En nuestro ejemplo, la inversión A tiene una TIR del cincuenta por ciento anual. La B, de apenas ocho coma cuatro por ciento anual. Misma ganancia, rendimientos muy distintos.

**5. Un caso con varios cobros**
Ahora veamos un caso más real, con varios cobros. Inviertes mil dólares hoy. Y recibes cuatrocientos dólares al final de cada año, durante tres años. En total cobras mil doscientos. ¿Cuál es el rendimiento anual? No es veinte por ciento, ni siete por ciento. La cuenta no es tan directa, porque cada cobro llega en un momento distinto.

**6. La tasa que deja la cuenta en cero**
Para resolverlo, se hace una pregunta: ¿a qué tasa tendría que descontar esos cobros futuros para que valgan exactamente los mil dólares que puse hoy? Si uso una tasa del cinco por ciento, los cobros valen más de mil: la inversión me deja ganancia extra. Si uso una tasa del quince por ciento, valen menos de mil: salgo perdiendo. En algún punto intermedio, la cuenta da exactamente cero. Esa tasa es la TIR. En este caso, nueve coma siete por ciento anual.

**7. Cómo se calcula**
La buena noticia es que no tienes que calcularla a mano. En Excel o en Google Sheets escribes los flujos en una columna: la inversión en negativo y los cobros en positivo. Y usas la función TIR. El resultado aparece al instante.

**8. Para qué sirve**
¿Y para qué sirve ese número? Para comparar. Si tienes una alternativa segura que rinde doce por ciento anual, un proyecto con TIR de nueve coma siete no te conviene. La regla general es simple: una inversión es atractiva cuando su TIR supera el rendimiento mínimo que tú le exiges.

**9. La TIR de un bono**
La TIR también es el número clave de los bonos. La TIR de un bono es el rendimiento anual que obtienes si lo compras al precio de hoy y lo mantienes hasta el vencimiento, cobrando todos los pagos. Imagina un bono que paga cien dólares dentro de un año. Si lo compras a noventa, tu TIR es de alrededor del once por ciento. Si el precio baja a ochenta, la TIR sube a veinticinco por ciento. Por eso se dice que el precio y la TIR de un bono se mueven al revés: cuando uno baja, la otra sube.

**10. Las tres trampas**
Pero cuidado: la TIR tiene tres trampas. Primera: supone que cada cobro lo reinviertes a esa misma tasa, y eso no siempre es posible. Segunda: no te dice el tamaño. Una TIR de cincuenta por ciento sobre cien dólares deja menos dinero que una de veinte por ciento sobre cien mil. Tercera, y la más importante: no mide el riesgo. Una TIR muy alta suele significar que el mercado duda de que te paguen.

**11. Cierre**
Volvamos al principio. Las inversiones A y B ganaban lo mismo, pero ahora sabes por qué la A es mucho mejor: te devuelve el dinero antes. La TIR resume eso en un solo número: cuánto rinde tu dinero por año. Úsala para comparar, pero nunca sola: mira también el plazo, el monto y el riesgo. Este video es educativo y no es una recomendación de inversión. Si te sirvió, suscríbete: en el próximo vemos cómo se analiza un bono paso a paso.

## Verificación de las cifras

| Dato | Cálculo |
|---|---|
| TIR de A = 50 % | 1.500 / 1.000 − 1 |
| TIR de B = 8,4 % | (1.500 / 1.000)^(1/5) − 1 = 8,45 % |
| «Casi seis veces» | 50 / 8,45 = 5,9 |
| TIR del caso con cobros = 9,7 % | −1.000 + 400/(1+r) + 400/(1+r)² + 400/(1+r)³ = 0 → r = 9,70 % |
| Valor a 5 % = +89 | 400 × 2,7232 − 1.000 |
| Valor a 15 % = −87 | 400 × 2,2832 − 1.000 |
| Bono a 90 → 11 % | 100 / 90 − 1 = 11,1 % |
| Bono a 80 → 25 % | 100 / 80 − 1 |

## Publicación (YouTube)

- **Título:** ¿Qué es la TIR (IRR)? Explicada en 5 minutos con un ejemplo simple
- **Alternativa:** Dos inversiones ganan lo mismo, pero una es 6 veces mejor: la TIR explicada
- **Descripción:**
  La TIR (tasa interna de retorno; en inglés, IRR o *internal rate of return*) es el número que permite comparar inversiones que ganan lo mismo en plazos distintos. En este video: qué mide, cómo se calcula en Excel o Google Sheets, cómo se aplica a los bonos y cuáles son sus tres limitaciones.

  00:00 Dos inversiones, la misma ganancia
  00:41 El valor del dinero en el tiempo
  01:03 Qué es la TIR (IRR)
  01:35 Un caso con varios cobros
  01:59 La tasa que deja la cuenta en cero
  02:33 Cómo se calcula en Excel
  02:50 Para qué sirve
  03:09 La TIR de un bono
  03:46 Las tres trampas de la TIR
  04:14 Resumen

  Contenido educativo. No constituye una recomendación de inversión.

  #finanzas #TIR #IRR #inversiones #educacionfinanciera #bonos
- Los capítulos corresponden al video final con la voz grabada (`largos/L01-tir/video.mp4`, 4 min 46 s).
