# Peso y masa en un minuto (vídeo vertical, 1080×1920)

Reel de 55 s con una manzana como protagonista. Pensado para 2.º de ESO (el curso
no aparece en pantalla). Marca @quantafyq y barra de tiempo arriba.

- `masa_peso_voz.mp4`: con narración sintética en español.
- `masa_peso.mp4`: sin voz, con subtítulos incrustados.
- `masa_peso.srt`: la narración como subtítulos.
- `generar_video.py`: script del vídeo. El estilo está en `../comun/reel.py`.

```bash
python3 generar_video.py                          # vídeo + .srt
python3 ../narrar.py masa_peso --voz <carpeta>    # versión con voz
```

## Guion

1. «¿Sabes cuál es la diferencia entre peso y masa? Te lo cuento en un minuto.»
2. **La masa:** la cantidad de manzana es la misma en la Tierra que en la Luna (0,2 kg). Se mide en kilogramos.
3. **El peso:** la fuerza con la que el planeta tira de la manzana. Se mide en newtons.
4. **La fórmula:** P = m · g.
5. **En la Tierra:** g = 9,8 → P = 0,2 · 9,8 = 1,96 N.
6. **En la Luna:** g = 1,6 → P = 0,2 · 1,6 = 0,32 N.
7. **Misma masa, distinto peso.**
8. **Recuerda:** la masa no cambia; el peso, sí.
