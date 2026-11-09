#!/usr/bin/env python3
"""
Vídeo: «Sólido, líquido y gas: el modelo cinético-corpuscular»

Explica de forma sencilla los tres estados de la materia según el modelo
cinético-corpuscular: cómo están ordenadas las partículas, cómo se mueven y
qué fuerzas hay entre ellas, y por qué eso explica la forma y el volumen.

Reutiliza las herramientas de dibujo de ../colisiones/generar_video.py.

Uso:
    python3 generar_video.py               # vídeo completo + subtítulos .srt
    python3 generar_video.py --preview 20  # fotograma PNG en el segundo 20
    python3 generar_video.py --hd720       # versión 1280x720
"""

import argparse
import math
import multiprocessing as mp
import os
import subprocess
import sys
import textwrap

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "colisiones"))
import generar_video as base  # noqa: E402
from generar_video import (  # noqa: E402
    BG, PANEL, GRID, WHITE, GREY, YELLOW, GREEN, RED, ORANGE, COL,
    W, H, FPS, Canvas, atom, fade, ramp, mix, clamp, check_mark, title,
)

# Colores de cada estado
C_SOL = (120, 200, 255)
C_LIQ = (70, 160, 255)
C_GAS = (255, 170, 90)

BOXW, BOXH, RP = 640, 540, 22     # recipiente y radio de partícula


# --------------------------------------------------------------------------
# Modelos de partículas
# --------------------------------------------------------------------------
def solid_positions(w, h, r):
    """Red ordenada (hexagonal) apoyada en el fondo del recipiente."""
    pts = []
    dx = 2 * r + 8
    dy = dx * math.sqrt(3) / 2
    cols, rows = 9, 7
    x_start = (w - (cols - 1) * dx - dx / 2) / 2
    for j in range(rows):
        for i in range(cols):
            x = x_start + i * dx + (dx / 2 if j % 2 else 0)
            y = h - r - 6 - j * dy
            pts.append((x, y))
    return np.array(pts)


SOLID = None
rng0 = np.random.default_rng(7)
PH = rng0.uniform(0, 2 * math.pi, (200, 4))
FR = rng0.uniform(4.0, 6.5, (200, 2))


def solid_frame(t, amp=3.5):
    p = SOLID.copy()
    p[:, 0] += amp * np.sin(FR[:len(p), 0] * t + PH[:len(p), 0])
    p[:, 1] += amp * np.sin(FR[:len(p), 1] * t + PH[:len(p), 1])
    return p


def simulate(n, w, h, r, sigma, g, dur, seed, start="bottom", cohesion=0.0):
    """Esferas duras en 2D con gravedad opcional y una atracción débil
    entre vecinas (`cohesion`) para que el líquido se mantenga unido."""
    rng = np.random.default_rng(seed)
    pos = []
    if start == "bottom":
        dx = 2 * r + 2
        cols = int((w - 2 * r) // dx)
        k = 0
        while len(pos) < n:
            j, i = divmod(k, cols)
            pos.append([r + 4 + i * dx + (r if j % 2 else 0), h - r - 4 - j * dx * 0.9])
            k += 1
    else:
        while len(pos) < n:
            p = np.array([rng.uniform(r * 1.5, w - r * 1.5), rng.uniform(r * 1.5, h - r * 1.5)])
            if all(np.hypot(*(p - q)) > 2.6 * r for q in pos):
                pos.append(p)
    pos = np.array(pos, dtype=float)
    vel = rng.normal(0, sigma, (n, 2))
    sub = 8
    dt = 1.0 / FPS / sub
    iu = np.triu_indices(n, 1)
    warm = int(2.0 * FPS)            # tiempo previo para que se asiente
    frames = []
    for f in range(warm + int(math.ceil(dur * FPS)) + 1):
        if f >= warm:
            frames.append(pos.copy())
        for _ in range(sub):
            vel[:, 1] += g * dt
            if cohesion:
                diff = pos[:, None, :] - pos[None, :, :]
                d = np.sqrt((diff ** 2).sum(-1)) + np.eye(n)
                m = (d > 2 * r) & (d < 3.2 * r)
                fmag = np.where(m, cohesion, 0.0)
                vel -= (fmag[:, :, None] * diff / d[:, :, None]).sum(1) * dt
            pos += vel * dt
            for k, size in ((0, w), (1, h)):
                lo = pos[:, k] < r
                hi = pos[:, k] > size - r
                pos[lo, k] = 2 * r - pos[lo, k]
                vel[lo, k] = np.abs(vel[lo, k])
                pos[hi, k] = 2 * (size - r) - pos[hi, k]
                vel[hi, k] = -np.abs(vel[hi, k])
            diff = pos[:, None, :] - pos[None, :, :]
            d2 = (diff ** 2).sum(-1)
            close = d2[iu] < (2 * r) ** 2
            for i, j in zip(iu[0][close], iu[1][close]):
                dv = pos[i] - pos[j]
                dist = math.hypot(*dv) or 1e-6
                nr = dv / dist
                vr = np.dot(vel[i] - vel[j], nr)
                ov = 2 * r - dist
                pos[i] += nr * ov / 2
                pos[j] -= nr * ov / 2
                if vr < 0:
                    vel[i] -= vr * nr
                    vel[j] += vr * nr
            # termostato suave: mantiene la «temperatura» constante
            v2 = (vel ** 2).mean()
            if v2 > 0:
                vel *= (1 + 0.02 * (sigma ** 2 / v2 - 1)) ** 0.5
    return frames


LIQ = GAS = None


def particles_at(state, t):
    if state == "sol":
        return solid_frame(t)
    frames = LIQ if state == "liq" else GAS
    return frames[min(int(t * FPS), len(frames) - 1)]


def draw_box(cv, state, t, x0, y0, s=1.0, color=C_LIQ, bonds=True, trails=False):
    w, h, r = BOXW * s, BOXH * s, RP * s
    # recipiente abierto por arriba (vaso), salvo el gas: recipiente cerrado
    cv.rect(x0, y0, x0 + w, y0 + h, fill=PANEL, radius=10)
    edge = mix(GRID, WHITE, 0.35)
    if state == "gas":
        cv.rect(x0 - 4, y0 - 4, x0 + w + 4, y0 + h + 4, outline=edge, width=6, radius=12)
    else:
        cv.line([(x0 - 3, y0 - 10), (x0 - 3, y0 + h + 3), (x0 + w + 3, y0 + h + 3),
                 (x0 + w + 3, y0 - 10)], edge, 6)
    p = particles_at(state, t) * s
    old = cv.bg
    cv.bg = PANEL
    if bonds and state != "gas":
        # fuerzas de atracción entre partículas vecinas (líneas)
        lim = (2 * RP + 18) * s if state == "sol" else (2 * RP + 6) * s
        col = mix(PANEL, YELLOW, 0.55 if state == "sol" else 0.3)
        n = len(p)
        for i in range(n):
            for j in range(i + 1, n):
                dx, dy = p[i, 0] - p[j, 0], p[i, 1] - p[j, 1]
                if dx * dx + dy * dy < lim * lim:
                    cv.line([(x0 + p[i, 0], y0 + p[i, 1]), (x0 + p[j, 0], y0 + p[j, 1])],
                            col, max(2, 4 * s))
    if trails and state == "gas":
        frames = GAS
        i1 = min(int(t * FPS), len(frames) - 1)
        i0 = max(0, i1 - 5)
        for a, b in zip(frames[i0] * s, frames[i1] * s):
            if np.hypot(*(a - b)) < 200 * s:
                cv.line([(x0 + a[0], y0 + a[1]), (x0 + b[0], y0 + b[1])], mix(PANEL, color, 0.35), r * 0.8)
    for x, y in p:
        _particle(cv, x0 + x, y0 + y, r, color)
    cv.bg = old


def _particle(cv, x, y, r, c):
    cv.circle(x, y, r, fill=mix(cv.bg, tuple(int(v * 0.55) for v in c), 1))
    cv.circle(x, y, r * 0.9, fill=c)
    cv.circle(x - r * 0.32, y - r * 0.34, r * 0.26, fill=tuple(int(v + (255 - v) * 0.5) for v in c))


# --------------------------------------------------------------------------
# Escenas
# --------------------------------------------------------------------------
def scene_title(cv, t, D):
    cv.text(W / 2, 300, "FÍSICA Y QUÍMICA", 34, mix(BG, GREY, fade(t, 0.2)), bold=True)
    cv.text(W / 2, 420, "Sólido, líquido y gas", 104, mix(BG, WHITE, fade(t, 0.4, 0.8)), bold=True)
    cv.text(W / 2, 540, "El modelo cinético-corpuscular", 56, mix(BG, YELLOW, fade(t, 1.1, 0.8)))
    a = fade(t, 1.8, 0.6)
    for k, (st, c) in enumerate((("sol", C_SOL), ("liq", C_LIQ), ("gas", C_GAS))):
        x = W / 2 + (k - 1) * 300
        for m in range(5):
            ang = m * 2 * math.pi / 5 + t * (0 if k == 0 else (0.8 * k))
            rr = (22 if k == 0 else 30 if k == 1 else 60) + (3 * math.sin(9 * t + m) if k == 0 else 0)
            _particle(cv, x + rr * math.cos(ang), 700 + rr * math.sin(ang), 14,
                      mix(BG, c, a))


POSTULADOS = [
    ("La materia está formada por partículas", "muy pequeñas que no podemos ver."),
    ("Entre las partículas hay espacio vacío.", ""),
    ("Las partículas están en continuo movimiento.", "Cuanto mayor es la temperatura, más rápido se mueven."),
    ("Entre las partículas hay fuerzas de atracción.", "Tienden a mantenerlas unidas."),
]


def scene_model(cv, t, D):
    title(cv, t, "El modelo cinético-corpuscular")
    for k, (a, b) in enumerate(POSTULADOS):
        t0 = 1.0 + k * 2.6
        al = fade(t, t0)
        y = 260 + k * 160
        cv.circle(330, y + 10, 38, fill=mix(BG, YELLOW, al))
        cv.text(330, y + 12, str(k + 1), 42, mix(BG, BG, al), bold=True)
        cv.text(400, y - 8, a, 46, mix(BG, WHITE, al), anchor="lm", bold=True)
        if b:
            cv.text(400, y + 42, b, 34, mix(BG, GREY, al), anchor="lm")


def state_scene(cv, t, state, name, color, props):
    cv.text(W / 2, 80, name, 72, mix(BG, color, fade(t, 0)), bold=True)
    x0, y0 = 170, 230
    draw_box(cv, state, t, x0, y0, 1.0, color=color)
    for k, (ttl, txt, t0) in enumerate(props):
        a = fade(t, t0)
        y = 260 + k * 150
        cv.rect(920, y - 10, 1800, y + 118, fill=mix(BG, PANEL, a), radius=16)
        cv.rect(920, y - 10, 932, y + 118, fill=mix(BG, color, a), radius=6)
        cv.text(960, y + 30, ttl, 40, mix(BG, WHITE, a), anchor="lm", bold=True)
        cv.text(960, y + 80, txt, 32, mix(BG, GREY, a), anchor="lm")


def scene_solid(cv, t, D):
    state_scene(cv, t, "sol", "SÓLIDO", C_SOL, [
        ("Muy juntas y ordenadas", "Forman una estructura regular", 1.0),
        ("Solo vibran", "No cambian de posición", 3.5),
        ("Fuerzas de atracción muy fuertes", "Las líneas amarillas las mantienen unidas", 6.0),
        ("Forma y volumen fijos", "No se pueden comprimir", 9.0),
    ])


def scene_liquid(cv, t, D):
    state_scene(cv, t, "liq", "LÍQUIDO", C_LIQ, [
        ("Juntas pero desordenadas", "No forman una estructura fija", 1.0),
        ("Se deslizan unas sobre otras", "Por eso los líquidos fluyen", 3.5),
        ("Fuerzas de atracción intermedias", "Más débiles que en el sólido", 6.0),
        ("Volumen fijo, forma variable", "Toman la forma del recipiente", 9.0),
    ])


def scene_gas(cv, t, D):
    state_scene(cv, t, "gas", "GAS", C_GAS, [
        ("Muy separadas y desordenadas", "Hay mucho espacio vacío entre ellas", 1.0),
        ("Se mueven libremente y muy rápido", "Chocan entre sí y con las paredes", 3.5),
        ("Fuerzas de atracción casi nulas", "Cada partícula va «a su aire»", 6.0),
        ("Ni forma ni volumen fijos", "Ocupan todo el recipiente y se comprimen", 9.0),
    ])


def scene_compare(cv, t, D):
    title(cv, t, "Comparación", y=70, size=60, color=WHITE)
    s = 0.78
    w = BOXW * s
    xs = [140, 140 + w + 90, 140 + 2 * (w + 90)]
    for x, (st, nm, c) in zip(xs, (("sol", "Sólido", C_SOL), ("liq", "Líquido", C_LIQ),
                                   ("gas", "Gas", C_GAS))):
        cv.text(x + w / 2, 165, nm, 46, c, bold=True)
        draw_box(cv, st, t, x, 210, s, color=c)
    a = fade(t, 2.5)
    y = 750
    cv.arrow(160, y, 1760, y, mix(BG, ORANGE, a), width=10, head=36)
    cv.text(W / 2, y - 40, "Al calentar: más movimiento, más separación y menos orden",
            38, mix(BG, ORANGE, a), bold=True)
    a = fade(t, 6.0)
    cv.text(W / 2, y + 65, "Fusión: sólido → líquido        Vaporización: líquido → gas",
            34, mix(BG, WHITE, a))


def scene_summary(cv, t, D):
    title(cv, t, "En resumen", y=100, size=70, color=YELLOW)
    rows = [("", "Sólido", "Líquido", "Gas"),
            ("Orden", "Ordenadas", "Desordenadas", "Muy desordenadas"),
            ("Movimiento", "Vibran", "Se deslizan", "Libre y rápido"),
            ("Fuerzas", "Muy fuertes", "Intermedias", "Casi nulas"),
            ("Forma", "Fija", "Variable", "Variable"),
            ("Volumen", "Fijo", "Fijo", "Variable")]
    xs = [400, 800, 1170, 1540]
    for k, row in enumerate(rows):
        a = fade(t, 0.6 + k * 0.9)
        y = 230 + k * 105
        if k:
            cv.rect(200, y - 44, 1740, y + 44, fill=mix(BG, PANEL, a), radius=12)
        for i, (x, s) in enumerate(zip(xs, row)):
            if k == 0:
                col = (C_SOL, C_LIQ, C_GAS)[i - 1] if i else WHITE
                cv.text(x, y, s, 44, mix(BG, col, a), bold=True)
            else:
                cv.text(x, y, s, 36 if i else 38, mix(PANEL, WHITE if i else YELLOW, a), bold=(i == 0))


def scene_end(cv, t, D):
    cv.text(W / 2, H / 2 - 30, "Sólido, líquido y gas", 80,
            mix(BG, WHITE, fade(t, 0.1, 0.6, D - 0.8, 0.6)), bold=True)
    cv.text(W / 2, H / 2 + 50, "El modelo cinético-corpuscular", 40,
            mix(BG, GREY, fade(t, 0.4, 0.6, D - 0.8, 0.6)))


# --------------------------------------------------------------------------
# Guion y narración
# --------------------------------------------------------------------------
SCENES = [
    (5.0, scene_title, [
        (1.2, "¿Por qué el hielo, el agua y el vapor son tan diferentes?")]),
    (13.0, scene_model, [
        (0.3, "Para explicarlo usamos el modelo cinético-corpuscular."),
        (3.3, "La materia está formada por partículas muy pequeñas, con espacio vacío entre ellas,"),
        (7.6, "que se mueven continuamente y se atraen entre sí.")]),
    (13.0, scene_solid, [
        (0.3, "En un sólido, las partículas están muy juntas y ordenadas."),
        (3.5, "No cambian de sitio: solo vibran en su posición."),
        (6.0, "Las fuerzas de atracción son muy fuertes,"),
        (9.0, "por eso los sólidos tienen forma y volumen fijos.")]),
    (13.0, scene_liquid, [
        (0.3, "En un líquido, las partículas siguen juntas, pero desordenadas."),
        (3.5, "Pueden deslizarse unas sobre otras: por eso los líquidos fluyen."),
        (6.0, "Las fuerzas de atracción son más débiles que en el sólido."),
        (9.0, "Los líquidos tienen volumen fijo, pero toman la forma del recipiente.")]),
    (13.0, scene_gas, [
        (0.3, "En un gas, las partículas están muy separadas."),
        (3.5, "Se mueven muy rápido y en todas direcciones, chocando entre sí y con las paredes."),
        (6.0, "Las fuerzas de atracción entre ellas son casi nulas."),
        (9.0, "Por eso un gas no tiene forma ni volumen fijos: ocupa todo el recipiente.")]),
    (12.0, scene_compare, [
        (0.3, "Si comparamos los tres estados…"),
        (2.5, "al calentar, las partículas se mueven más rápido, se separan y pierden el orden."),
        (6.5, "Así una sustancia pasa de sólido a líquido (fusión) y de líquido a gas (vaporización).")]),
    (11.0, scene_summary, [
        (0.3, "En resumen: el estado de una sustancia depende de cómo están ordenadas sus partículas,"),
        (5.0, "de cómo se mueven y de la fuerza con que se atraen.")]),
    (4.0, scene_end, []),
]

STARTS, _acc = [], 0.0
for _d, _f, _c in SCENES:
    STARTS.append(_acc)
    _acc += _d
TOTAL = _acc
CAPS = []
for (d, _, caps), s in zip(SCENES, STARTS):
    for k, (t0, txt) in enumerate(caps):
        t1 = caps[k + 1][0] if k + 1 < len(caps) else d - 0.2
        CAPS.append((s + t0, s + t1, txt))


def draw_caption(cv, T):
    for (t0, t1, txt) in CAPS:
        if t0 <= T < t1:
            a = fade(T, t0, 0.25, t_out=t1 - 0.25, dur_out=0.25)
            lines = textwrap.wrap(txt, 64)
            hh = 50 * len(lines) + 30
            y0 = 1040 - hh
            cv.rect(160, y0, 1760, 1040, fill=mix(BG, (6, 9, 18), a), radius=14)
            for k, ln in enumerate(lines):
                cv.text(W / 2, y0 + 40 + k * 50, ln, 36, mix((6, 9, 18), WHITE, a))
            break


def render(T):
    cv = Canvas()
    for (d, f, _), s in zip(SCENES, STARTS):
        if s <= T < s + d:
            t = T - s
            f(cv, t, d)
            break
    draw_caption(cv, T)
    img = cv.final()
    for s, (d, _, _) in zip(STARTS, SCENES):
        if s <= T < s + d:
            t = T - s
            k = min(ramp(t, 0, 0.25), 1 - ramp(t, d - 0.25, d))
            if k < 1:
                img = Image.blend(Image.new("RGB", img.size, BG), img, k)
            break
    return img


def render_frame(i):
    return render(i / FPS).tobytes()


def build():
    global SOLID, LIQ, GAS
    SOLID = solid_positions(BOXW, BOXH, RP)
    dur = 14.0
    LIQ = simulate(63, BOXW, BOXH, RP, 110, 900, dur, seed=2, start="bottom", cohesion=600)
    GAS = simulate(14, BOXW, BOXH, RP, 300, 0, dur, seed=4, start="random")


def write_srt(path):
    def ts(x):
        ms = int(round(x * 1000))
        h, ms = divmod(ms, 3600000)
        m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    with open(path, "w", encoding="utf-8") as fh:
        for k, (t0, t1, txt) in enumerate(CAPS, 1):
            fh.write(f"{k}\n{ts(t0)} --> {ts(t1)}\n{txt}\n\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", type=float, nargs="*")
    ap.add_argument("--hd720", action="store_true")
    ap.add_argument("-o", "--output", default=os.path.join(HERE, "estados_materia.mp4"))
    args = ap.parse_args()
    if args.hd720:
        base.OUT_SCALE = 2 / 3
    build()
    print(f"Duración total: {TOTAL:.1f} s")
    if args.preview is not None:
        for s in args.preview:
            p = os.path.join(HERE, f"preview_{s:05.1f}.png")
            render(s).save(p)
            print("guardado", p)
        return
    srt = os.path.splitext(args.output)[0] + ".srt"
    write_srt(srt)
    nfr = int(TOTAL * FPS)
    ow, oh = int(W * base.OUT_SCALE), int(H * base.OUT_SCALE)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{ow}x{oh}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", args.output]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with mp.get_context("fork").Pool(os.cpu_count()) as pool:
        for k, buf in enumerate(pool.imap(render_frame, range(nfr), chunksize=4)):
            proc.stdin.write(buf)
            if k % 300 == 0:
                print(f"  fotograma {k}/{nfr}", flush=True)
    proc.stdin.close()
    proc.wait()
    print("vídeo:", args.output, "\nsubtítulos:", srt)


if __name__ == "__main__":
    main()
