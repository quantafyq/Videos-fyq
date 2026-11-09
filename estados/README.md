# Sólido, líquido y gas: el modelo cinético-corpuscular

Vídeo sencillo (1:24, 1920×1080, sin audio, con subtítulos incrustados).

- `estados_materia.mp4` – el vídeo.
- `estados_materia.srt` – la narración como subtítulos.
- `generar_video.py` – script que lo genera (usa las herramientas de dibujo de
  `../colisiones/generar_video.py`). Los textos están en la lista `SCENES`.

```bash
python3 generar_video.py               # regenera vídeo y .srt
python3 generar_video.py --preview 25  # PNG del segundo 25
```

## Guion

| Tiempo | Escena | Idea clave |
|---|---|---|
| 0:00 | Título | ¿Por qué el hielo, el agua y el vapor son tan diferentes? |
| 0:05 | Modelo cinético-corpuscular | Partículas muy pequeñas, espacio vacío entre ellas, movimiento continuo (más rápido a más temperatura) y fuerzas de atracción. |
| 0:18 | Sólido | Partículas juntas y ordenadas que solo vibran; fuerzas muy fuertes; forma y volumen fijos. |
| 0:31 | Líquido | Juntas pero desordenadas, se deslizan; fuerzas intermedias; volumen fijo y forma del recipiente. |
| 0:44 | Gas | Muy separadas, movimiento rápido y libre; fuerzas casi nulas; ocupan todo el recipiente. |
| 0:57 | Comparación | Al calentar: más movimiento, más separación, menos orden (fusión y vaporización). |
| 1:09 | Resumen | Tabla: orden, movimiento, fuerzas, forma y volumen. |

Nota: en el gas se han dibujado pocas partículas para que se vea el espacio
vacío; en un gas real la separación es todavía mucho mayor.

## Versión con voz

`estados_materia_voz.mp4` es el mismo vídeo con narración sintética en español.
Se genera con `python3 ../narrar.py estados --voz <carpeta de la voz>`
(ver instrucciones en `narrar.py`).
