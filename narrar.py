#!/usr/bin/env python3
"""
Añade voz (narración sintética en español) a un vídeo de este repositorio.

Lee los textos de narración (CAPS) del script del vídeo, sintetiza cada frase
con una voz Piper (motor sherpa-onnx) y la coloca en el instante en que
aparece su subtítulo. Después une el audio con el vídeo.

Requisitos:
    pip install sherpa-onnx numpy
    Voz: https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-es_ES-davefx-medium.tar.bz2
         (descomprimir y pasar la carpeta con --voz)

Uso:
    python3 narrar.py colisiones --voz /ruta/vits-piper-es_ES-davefx-medium
    python3 narrar.py estados    --voz /ruta/vits-piper-es_ES-davefx-medium

Genera <carpeta>/<video>_voz.mp4 (vídeo con voz y subtítulos incrustados).

En oxisales y sales_acidas, para que la voz vaya sincronizada con la animación:
    python3 narrar.py oxisales --voz ... --medir   # guarda oxisales/narracion.json
    (cd oxisales && python3 generar_video.py)      # el vídeo se alarga donde haga falta
    python3 narrar.py oxisales --voz ...           # añade la voz
"""

import argparse
import glob
import importlib.util
import json
import os
import re
import subprocess
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def load_module(folder):
    path = os.path.join(HERE, folder, "generar_video.py")
    sys.path.insert(0, os.path.join(HERE, "colisiones"))
    spec = importlib.util.spec_from_file_location(f"video_{folder}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def spoken(text):
    """Adapta el texto escrito para que la voz lo lea bien."""
    t = text
    rep = [
        ("(III)", " tres"), ("(II)", " dos"), ("(IV)", " cuatro"), ("(I)", " uno"),
        ("A₂", "A dos"), ("B₂", "B dos"), ("2 AB", "dos A B"),
        ("A–A", "A A"), ("B–B", "B B"), ("A–B", "A B"), ("AB", "A B"),
        ("Ea", "E a"), ("≥", "mayor o igual que"), ("…", "..."),
    ]
    for a, b in rep:
        t = t.replace(a, b)
    t = re.sub(r"\(([^)]*)\)", r", \1,", t)
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("carpeta", choices=["colisiones", "estados", "oxisales", "sales_acidas", "oxidos", "masa_peso"])
    ap.add_argument("--voz", required=True, help="carpeta de la voz Piper")
    ap.add_argument("--velocidad", type=float, default=1.0)
    ap.add_argument("--medir", action="store_true",
                    help="solo mide cuánto dura cada frase y lo guarda en narracion.json")
    args = ap.parse_args()

    import sherpa_onnx

    onnx = glob.glob(os.path.join(args.voz, "*.onnx"))[0]
    cfg = sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                model=onnx,
                tokens=os.path.join(args.voz, "tokens.txt"),
                data_dir=os.path.join(args.voz, "espeak-ng-data"),
            ),
            num_threads=4,
        ),
    )
    tts = sherpa_onnx.OfflineTts(cfg)

    mod = load_module(args.carpeta)
    caps, total = mod.CAPS, mod.TOTAL
    sr = None
    clips = []
    for cap in caps:
        t0, t1 = cap[0], cap[1]
        txt = cap[3] if len(cap) > 3 else cap[2]
        speed = args.velocidad
        audio = tts.generate(spoken(txt), sid=0, speed=speed)
        sr = audio.sample_rate
        samples = np.array(audio.samples, dtype=np.float32)
        dur = len(samples) / sr
        clips.append((t0, samples, txt))

    if args.medir:
        jp = os.path.join(HERE, args.carpeta, "narracion.json")
        with open(jp, "w", encoding="utf-8") as fh:
            json.dump({"durs": [round(len(c[1]) / sr, 3) for c in clips]}, fh)
        print("duraciones guardadas en", jp)
        return

    track = np.zeros(int((total + 1) * sr), dtype=np.float32)
    cursor = 0
    for t0, s, txt in clips:
        start = max(int((t0 + 0.1) * sr), cursor)  # nunca pisar la frase anterior
        retraso = start / sr - t0 - 0.1
        aviso = f"  (empieza {retraso:.1f} s tarde)" if retraso > 0.05 else ""
        print(f"{t0:6.1f}s  {len(s) / sr:4.1f}s  {txt[:60]}{aviso}")
        end = min(len(track), start + len(s))
        track[start:end] += s[: end - start]
        cursor = end + int(0.1 * sr)
    track = track[: int(total * sr)]
    track /= max(1e-6, np.abs(track).max()) / 0.9

    base = os.path.join(HERE, args.carpeta)
    video = [f for f in glob.glob(os.path.join(base, "*.mp4")) if not f.endswith("_voz.mp4")][0]
    wav = os.path.splitext(video)[0] + "_voz.wav"
    with wave.open(wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((track * 32767).astype(np.int16).tobytes())
    out = os.path.splitext(video)[0] + "_voz.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", wav,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest",
                    "-movflags", "+faststart", out], check=True)
    os.remove(wav)
    print("vídeo con voz:", out)


if __name__ == "__main__":
    main()
