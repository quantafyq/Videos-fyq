# Óxidos (vídeo vertical, 1080×1920)

Vídeo en formato reel (2 min 27 s) con estilo de fondo crema, titulares gruesos
con bloques naranjas, ilustraciones planas y pegatinas. Marca @quantafyq.

- `oxidos_voz.mp4`: con narración sintética en español.
- `oxidos.mp4`: sin voz, con subtítulos incrustados.
- `oxidos.srt`: la narración como subtítulos.
- `generar_video.py`: script del vídeo. El estilo está en `../comun/reel.py`.
- `narracion.json`: duración de cada frase hablada, para sincronizar voz y animación.

```bash
python3 generar_video.py                       # vídeo + .srt
python3 ../narrar.py oxidos --voz <carpeta>    # versión con voz
```

## Contenido

1. **Gancho:** un clavo oxidado, las burbujas de un refresco y la arena son óxidos (Fe₂O₃, CO₂, SiO₂).
2. **Qué es un óxido:** oxígeno + otro elemento; el oxígeno actúa con −2.
3. **Dos tipos:** óxido metálico (Fe₂O₃) y óxido no metálico (CO₂).
4. **Formular:** el más electronegativo va a la derecha; los números de oxidación se escriben encima de cada símbolo, se cruzan (Fe₂O₃) y se simplifica si se puede (CaO).
5. **Nombrar:** de derecha a izquierda, con prefijos (trióxido de dihierro) o con número de oxidación (óxido de hierro(III)).
6. **Más ejemplos:** CO, CO₂ y CaO.
7. **Ojo con los halógenos:** OCl₂ es dicloruro de oxígeno.
8. **Tu turno:** Al₂O₃ y óxido de cobre(I), con cuenta atrás.
9. **Resumen.**

Tipografía: Archivo (licencia OFL, en `../comun/fuentes/`).
