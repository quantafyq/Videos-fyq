# Masa y peso (vídeo vertical, 1080×1920)

Vídeo en formato reel (1 min 51 s), pensado para 2.º de ESO (el curso no aparece
en pantalla). Marca @quantafyq.

- `masa_peso_voz.mp4`: con narración sintética en español.
- `masa_peso.mp4`: sin voz, con subtítulos incrustados.
- `masa_peso.srt`: la narración como subtítulos.
- `generar_video.py`: script del vídeo. El estilo está en `../comun/reel.py`.

```bash
python3 generar_video.py                          # vídeo + .srt
python3 ../narrar.py masa_peso --voz <carpeta>    # versión con voz
```

## Contenido

1. **Gancho:** «¿Cuánto pesas?» «50 kilos» no es tu peso: es tu masa.
2. **La masa:** cantidad de materia; se mide en kg con una balanza; no cambia.
3. **El peso:** fuerza con que te atrae la Tierra; se mide en N con un dinamómetro; cambia según el lugar.
4. **La fórmula:** P = m · g, con el significado y la unidad de cada letra (g = 9,8 N/kg en la Tierra).
5. **En la Tierra:** 50 kg → P = 50 · 9,8 = 490 N.
6. **En la Luna:** g = 1,6 N/kg → P = 80 N, con la misma masa.
7. **Comparación** masa/peso en dos columnas.
8. **Tu turno:** una mochila de 5 kg pesa 49 N.
9. **Resumen.**
