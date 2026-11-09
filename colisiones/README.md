# Teoría de colisiones: ¿cuándo ocurre una reacción química?

Vídeo didáctico (≈2 min, 1920×1080, 30 fps) que explica con el choque de dos
partículas cuándo se produce una reacción química.

- `teoria_colisiones.mp4` – el vídeo (sin audio, con subtítulos incrustados).
- `teoria_colisiones.srt` – la narración como subtítulos (para doblar con voz o
  añadirlos en YouTube).
- `generar_video.py` – script que genera el vídeo (Python 3 + numpy + Pillow + ffmpeg).

```bash
python3 generar_video.py               # regenera el vídeo y el .srt
python3 generar_video.py --hd720       # versión 1280×720
python3 generar_video.py --preview 55  # PNG del segundo 55 (para revisar)
```

Los textos de la narración están en la lista `SCENES` del script: se pueden
cambiar y volver a generar el vídeo.

## Guion

| Tiempo | Escena | Idea clave |
|---|---|---|
| 0:00 | Título | ¿Qué tiene que pasar para que ocurra una reacción química? |
| 0:06 | ¿Qué es una reacción? | A₂ + B₂ → 2 AB: se rompen enlaces y se forman otros nuevos; los átomos se reorganizan. |
| 0:16 | Partículas en movimiento | Las partículas se mueven y chocan continuamente. Para reaccionar, primero tienen que chocar. |
| 0:26 | Condiciones | No todos los choques son eficaces: hace falta **energía suficiente** y **orientación adecuada**. |
| 0:33 | Caso 1 | Choque con poca energía (E < Ea): rebotan, no hay reacción. |
| 0:43 | Caso 2 | Choque con energía pero «de punta» (mala orientación): rebotan, no hay reacción. |
| 0:53 | Caso 3 | Energía suficiente + orientación adecuada: se rompen A–A y B–B y se forman dos A–B. ¡Choque eficaz! |
| 1:04 | Energía de activación | Diagrama de energía: reactivos, complejo activado, productos. Si E < Ea la partícula vuelve atrás; si E ≥ Ea supera la barrera. |
| 1:18 | Temperatura | Más temperatura → partículas más rápidas → más choques y más energéticos → más choques eficaces. |
| 1:33 | Concentración | Más partículas en el mismo volumen → más choques por segundo → reacción más rápida. |
| 1:46 | Resumen | Chocar + energía ≥ Ea + orientación adecuada. |

## Notas para el aula

- Las moléculas A₂, B₂ y AB son genéricas, para no ligar la explicación a una
  reacción concreta.
- En las simulaciones de temperatura y concentración cada partícula se dibuja
  como una esfera y el producto AB en morado (simplificación). Un choque A–B es
  eficaz si la velocidad relativa supera un umbral (energía ≥ Ea) y, además, la
  orientación es la adecuada (se decide al azar, 50 %). Los números de choques
  eficaces salen de la propia simulación.
- Preguntas para después del vídeo: ¿por qué se guardan los alimentos en la
  nevera? ¿Por qué arde antes la madera en virutas que un tronco? (superficie de
  contacto, otro factor que se puede introducir después).

## Versión con voz

`teoria_colisiones_voz.mp4` es el mismo vídeo con narración sintética en
español. Se genera con `python3 ../narrar.py colisiones --voz <carpeta de la voz>`
(ver instrucciones en `narrar.py`).
