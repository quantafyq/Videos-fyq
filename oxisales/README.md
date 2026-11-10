# Oxisales: formular y nombrar (1.º Bachillerato)

- `oxisales.mp4`: vídeo sin voz, con subtítulos incrustados.
- `oxisales_voz.mp4`: el mismo vídeo con narración sintética en español.
- `oxisales.srt`: la narración como subtítulos.
- `generar_video.py`: script que genera el vídeo. Usa `../comun/formulacion.py`.

```bash
python3 generar_video.py                         # vídeo + .srt
python3 ../narrar.py oxisales --voz <carpeta>    # versión con voz
```

## Contenido

1. **¿Qué es una oxisal?** Se sustituyen los H de un oxoácido por un metal: H₂SO₄ → CuSO₄.
2. **Recuerda los oxoácidos:** hipo–oso, –oso, –ico y per–ico, con el ejemplo del cloro.
3. **Del ácido al anión:** –oso pasa a –ito y –ico pasa a –ato («cuando el oso toca el pito, Perico toca el silbato»).
4. **Tabla de aniones:** hipoclorito, clorito, clorato, perclorato, sulfito, sulfato, nitrito, nitrato, carbonato, fosfato y permanganato. La carga del anión es igual al número de H que pierde el ácido.
5. **Formular en cuatro pasos**, con tres ejemplos:
   - nitrato de potasio → KNO₃;
   - sulfato de hierro(III) → Fe₂(SO₄)₃, con cruce de cargas y paréntesis;
   - carbonato de calcio → CaCO₃, con simplificación.
6. **Nombrar**, con dos ejemplos: CuSO₄ → sulfato de cobre(II) y Fe(NO₂)₂ → nitrito de hierro(II).
7. **Cuatro ejercicios** con cuenta atrás y solución: KClO₃, Al₂(SO₄)₃, NaClO y Ca₃(PO₄)₂.
8. **Resumen.**

Se usa la nomenclatura tradicional (sulfato de cobre(II)), que la IUPAC acepta. La de
adición, del tipo tetraoxidosulfato(2−) de cobre(2+), no aparece en el vídeo.

`narracion.json` guarda cuánto dura cada frase hablada; con él, el vídeo se alarga donde hace falta para que la voz vaya sincronizada (ver `../narrar.py`).
