#!/usr/bin/env python3
"""
Vídeo: «Teoría de colisiones: ¿cuándo ocurre una reacción química?»

Genera un vídeo MP4 (1920x1080, 30 fps) que explica, mediante el choque de
partículas, las condiciones para que se produzca una reacción química:

  1. Las partículas tienen que chocar.
  2. El choque debe tener energía suficiente (≥ energía de activación, Ea).
  3. El choque debe producirse con la orientación adecuada.

Además muestra el diagrama de energía (Ea, complejo activado) y cómo la
temperatura y la concentración aumentan el número de choques eficaces.

Requisitos: Python 3, numpy, Pillow y ffmpeg en el PATH.

Uso:
    python3 generar_video.py               # vídeo completo
    python3 generar_video.py --preview 30  # fotograma PNG en el segundo 30
    python3 generar_video.py --hd720       # versión 1280x720 (más rápida)

Se generan también los subtítulos (.srt) con el texto de la narración.
"""

import argparse
import math
import multiprocessing as mp
import os
import subprocess
import sys
import textwrap

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------
# Configuración general
# --------------------------------------------------------------------------
W, H = 1920, 1080          # coordenadas lógicas (siempre 1920x1080)
SS = 2                      # supermuestreo para antialiasing
FPS = 30
OUT_SCALE = 1.0             # 1.0 -> 1920x1080, 2/3 -> 1280x720

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Paleta
BG = (13, 19, 36)
PANEL = (24, 33, 58)
GRID = (52, 64, 98)
WHITE = (240, 244, 250)
GREY = (150, 160, 185)
YELLOW = (255, 210, 80)
GREEN = (90, 215, 130)
RED = (245, 95, 95)
ORANGE = (255, 160, 70)
COL = {"A": (239, 96, 96), "B": (70, 160, 255), "P": (178, 115, 240)}
BOND = (205, 212, 228)


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, t):
    return a + (b - a) * t


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ramp(t, t0, t1):
    """0 antes de t0, 1 después de t1, suave entre medias."""
    if t1 <= t0:
        return 1.0 if t >= t0 else 0.0
    return ease((t - t0) / (t1 - t0))


def fade(t, t_in, dur=0.6, t_out=None, dur_out=0.4):
    a = ramp(t, t_in, t_in + dur)
    if t_out is not None:
        a *= 1 - ramp(t, t_out, t_out + dur_out)
    return a


def mix(c1, c2, a):
    a = clamp(a)
    return tuple(int(round(c1[i] + (c2[i] - c1[i]) * a)) for i in range(3))


def shade(c, k):
    return tuple(int(v * k) for v in c)


def tint(c, k):
    return tuple(int(v + (255 - v) * k) for v in c)


_fonts = {}


def font(size, bold=False):
    key = (int(size * SS), bold)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(FONT_BOLD if bold else FONT_REG, key[0])
    return _fonts[key]


class Canvas:
    """Lienzo con coordenadas lógicas 1920x1080 y supermuestreo."""

    def __init__(self, bg=BG):
        self.bg = bg
        self.img = Image.new("RGB", (W * SS, H * SS), bg)
        self.d = ImageDraw.Draw(self.img)

    @staticmethod
    def _p(x, y):
        return (x * SS, y * SS)

    def circle(self, x, y, r, fill=None, outline=None, width=0):
        self.d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS],
                       fill=fill, outline=outline, width=int(width * SS))

    def line(self, pts, fill, width=4):
        self.d.line([self._p(*p) for p in pts], fill=fill,
                    width=max(1, int(width * SS)), joint="curve")

    def poly(self, pts, fill):
        self.d.polygon([self._p(*p) for p in pts], fill=fill)

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, width=0, radius=0):
        self.d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS],
                                 radius=radius * SS, fill=fill, outline=outline,
                                 width=int(width * SS))

    def text(self, x, y, s, size, fill, anchor="mm", bold=False):
        self.d.text(self._p(x, y), s, font=font(size, bold), fill=fill, anchor=anchor)

    def text_width(self, s, size, bold=False):
        return font(size, bold).getlength(s) / SS

    def arrow(self, x0, y0, x1, y1, fill, width=6, head=22):
        ang = math.atan2(y1 - y0, x1 - x0)
        bx = x1 - head * math.cos(ang)
        by = y1 - head * math.sin(ang)
        self.line([(x0, y0), (bx, by)], fill, width)
        left = (bx + head * 0.55 * math.cos(ang + math.pi / 2),
                by + head * 0.55 * math.sin(ang + math.pi / 2))
        right = (bx + head * 0.55 * math.cos(ang - math.pi / 2),
                 by + head * 0.55 * math.sin(ang - math.pi / 2))
        self.poly([(x1, y1), left, right], fill)

    def dashed(self, x0, y0, x1, y1, fill, width=3, dash=14, gap=10):
        L = math.hypot(x1 - x0, y1 - y0)
        if L == 0:
            return
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        s = 0.0
        while s < L:
            e = min(L, s + dash)
            self.line([(x0 + ux * s, y0 + uy * s), (x0 + ux * e, y0 + uy * e)], fill, width)
            s += dash + gap

    def glow(self, x, y, r, color, a):
        """Halo luminoso (dibujar antes que los objetos que queden delante)."""
        if a <= 0:
            return
        steps = 7
        for k in range(steps, 0, -1):
            rr = r * (0.35 + 0.65 * k / steps)
            self.circle(x, y, rr, fill=mix(self.bg, color, a * (1 - k / (steps + 1)) ** 1.3))

    def final(self):
        img = self.img.reduce(SS)
        if OUT_SCALE != 1.0:
            img = img.resize((int(W * OUT_SCALE), int(H * OUT_SCALE)), Image.LANCZOS)
        return img


# --------------------------------------------------------------------------
# Dibujo de átomos y moléculas
# --------------------------------------------------------------------------
def atom(cv, x, y, kind, r=45, a=1.0, label=None, bg=None):
    bg = bg or cv.bg
    c = COL[kind]
    cv.circle(x, y, r, fill=mix(bg, shade(c, 0.55), a))
    cv.circle(x, y, r * 0.9, fill=mix(bg, c, a))
    cv.circle(x - r * 0.32, y - r * 0.34, r * 0.26, fill=mix(bg, tint(c, 0.45), a))
    if label is None:
        label = "AB" if kind == "P" else kind
    if label:
        size = r * (0.62 if len(label) > 1 else 0.85)
        cv.text(x + r * 0.04, y + r * 0.06, label, size, mix(bg, WHITE, a), bold=True)


def bond(cv, p1, p2, a=1.0, width=16, color=BOND):
    if a <= 0:
        return
    cv.line([p1, p2], mix(cv.bg, color, a), width)


def diatomic(cv, x, y, k1, k2, ang=0.0, d=95, r=45, a=1.0):
    """Molécula diatómica centrada en (x, y) con ángulo `ang` (radianes)."""
    dx, dy = math.cos(ang) * d / 2, math.sin(ang) * d / 2
    p1, p2 = (x - dx, y - dy), (x + dx, y + dy)
    bond(cv, p1, p2, a)
    atom(cv, *p1, k1, r=r, a=a)
    atom(cv, *p2, k2, r=r, a=a)


def check_mark(cv, x, y, s, color, w=10):
    cv.line([(x - s * 0.5, y), (x - s * 0.15, y + s * 0.35), (x + s * 0.55, y - s * 0.45)], color, w)


def cross_mark(cv, x, y, s, color, w=10):
    cv.line([(x - s / 2, y - s / 2), (x + s / 2, y + s / 2)], color, w)
    cv.line([(x - s / 2, y + s / 2), (x + s / 2, y - s / 2)], color, w)


def title(cv, t, s, y=90, size=58, color=WHITE, t0=0.0):
    cv.text(W / 2, y, s, size, mix(cv.bg, color, fade(t, t0, 0.6)), bold=True)


def burst(cv, x, y, age, big=True):
    """Destello de un choque eficaz (estrella amarilla)."""
    life = 0.7 if big else 0.35
    if age < 0 or age > life:
        return
    u = age / life
    a = 1 - u
    R = (26 + 55 * u) if big else (14 + 22 * u)
    col = YELLOW if big else WHITE
    if big:
        cv.glow(x, y, R * 1.3, YELLOW, a * 0.8)
        pts = []
        for k in range(16):
            ang = k * math.pi / 8 + 0.3
            rr = R if k % 2 == 0 else R * 0.45
            pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang)))
        cv.poly(pts, mix(cv.bg, col, a))
    else:
        cv.circle(x, y, R, outline=mix(cv.bg, col, a * 0.7), width=3)


# --------------------------------------------------------------------------
# Simulación de un gas de partículas (choques elásticos en 2D)
# --------------------------------------------------------------------------
def simulate(nA, nB, w, h, r, sigma, dur, seed, thr=1e9, p_orient=0.5, react=False):
    """Devuelve posiciones/tipos por fotograma y la lista de choques.

    Un choque A–B es eficaz si la componente normal de la velocidad relativa
    supera `thr` (energía suficiente) y, además, la orientación es adecuada
    (probabilidad `p_orient`). Si `react` es True, las dos partículas pasan
    a ser producto (AB, tipo 2) y ya no reaccionan más.
    """
    rng = np.random.default_rng(seed)
    n = nA + nB
    pos = []
    while len(pos) < n:
        p = np.array([rng.uniform(r * 1.5, w - r * 1.5), rng.uniform(r * 1.5, h - r * 1.5)])
        if all(np.hypot(*(p - q)) > 2.6 * r for q in pos):
            pos.append(p)
    pos = np.array(pos, dtype=float)
    vel = rng.normal(0, sigma, (n, 2))
    types = np.array([0] * nA + [1] * nB)
    rng.shuffle(types)
    frames, events = [], []
    sub = 6
    dt = 1.0 / FPS / sub
    nfr = int(math.ceil(dur * FPS)) + 1
    iu = np.triu_indices(n, 1)
    for f in range(nfr):
        frames.append((pos.copy(), types.copy()))
        for _ in range(sub):
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
                dvec = pos[i] - pos[j]
                dist = math.hypot(*dvec) or 1e-6
                nrm = dvec / dist
                vrel = np.dot(vel[i] - vel[j], nrm)
                if vrel >= 0:
                    continue
                vel[i] -= vrel * nrm
                vel[j] += vrel * nrm
                ov = 2 * r - dist
                pos[i] += nrm * ov / 2
                pos[j] -= nrm * ov / 2
                mid = (pos[i] + pos[j]) / 2
                eff = False
                if react and {types[i], types[j]} == {0, 1} and -vrel > thr:
                    if rng.random() < p_orient:
                        eff = True
                        types[i] = types[j] = 2
                events.append(((f + 0.5) / FPS, mid[0], mid[1], eff))
    return frames, events


def draw_sim(cv, sim, t, x0, y0, w, h, r, show_minor=True, label_size=None):
    frames, events = sim
    cv.rect(x0 - 6, y0 - 6, x0 + w + 6, y0 + h + 6, fill=PANEL, outline=GRID, width=3, radius=14)
    old_bg = cv.bg
    cv.bg = PANEL
    for (te, ex, ey, eff) in events:
        age = t - te
        if -0.01 < age < 0.75:
            if eff:
                burst(cv, x0 + ex, y0 + ey, age, big=True)
            elif show_minor:
                burst(cv, x0 + ex, y0 + ey, age, big=False)
    idx = min(int(t * FPS), len(frames) - 1)
    pos, types = frames[idx]
    names = ("A", "B", "P")
    for (px, py), ty in zip(pos, types):
        k = names[ty]
        atom(cv, x0 + px, y0 + py, k, r=r, label="" if (k == "P" and r < 22) else k)
    cv.bg = old_bg


def count_eff(sim, t):
    return sum(1 for e in sim[1] if e[3] and e[0] <= t)


def count_all(sim, t):
    return sum(1 for e in sim[1] if e[0] <= t)


# --------------------------------------------------------------------------
# Escenas
# --------------------------------------------------------------------------
def scene_title(cv, t, D):
    # partículas flotando de fondo
    for k in range(14):
        kind = "AB"[k % 2]
        x = (k * 157 + 60 * t * (1 + (k % 3) * 0.3)) % (W + 200) - 100
        y = 140 + (k * 97) % 800 + 30 * math.sin(t * 0.8 + k)
        atom(cv, x, y, kind, r=22 + (k % 3) * 6, a=0.22 * fade(t, 0, 1.2))
    cv.text(W / 2, 330, "FÍSICA Y QUÍMICA", 34, mix(BG, GREY, fade(t, 0.2)), bold=True)
    cv.text(W / 2, 450, "Teoría de colisiones", 104, mix(BG, WHITE, fade(t, 0.4, 0.8)), bold=True)
    cv.text(W / 2, 570, "¿Cuándo ocurre una reacción química?", 56, mix(BG, YELLOW, fade(t, 1.1, 0.8)))
    # pequeño choque decorativo
    u = ramp(t, 2.0, 3.6)
    xa = lerp(560, 905, u)
    xb = lerp(1360, 1015, u)
    a = fade(t, 1.8, 0.5)
    if t > 3.6:
        burst(cv, 960, 720, t - 3.6)
    if t < 3.6:
        atom(cv, xa, 720, "A", r=34, a=a)
        atom(cv, xb, 720, "B", r=34, a=a)
    else:
        u2 = ramp(t, 3.6, 4.4)
        diatomic(cv, 960, 720, "A", "B", d=lerp(110, 72, u2), r=34)


def scene_what_is(cv, t, D):
    title(cv, t, "¿Qué es una reacción química?")
    r, d, y = 40, 80, 430
    a1 = fade(t, 0.6)
    diatomic(cv, 390, y, "A", "A", d=d, r=r, a=a1)
    cv.text(560, y, "+", 70, mix(BG, WHITE, a1), bold=True)
    diatomic(cv, 730, y, "B", "B", d=d, r=r, a=a1)
    a2 = fade(t, 1.6)
    cv.arrow(870, y, 1040, y, mix(BG, WHITE, a2), width=8, head=30)
    a3 = fade(t, 2.4)
    diatomic(cv, 1180, y, "A", "B", d=d, r=r, a=a3)
    cv.text(1350, y, "+", 70, mix(BG, WHITE, a3), bold=True)
    diatomic(cv, 1520, y, "A", "B", d=d, r=r, a=a3)

    cv.text(560, 540, "A₂ + B₂", 46, mix(BG, WHITE, a1), bold=True)
    cv.text(1350, 540, "2 AB", 46, mix(BG, WHITE, a3), bold=True)
    cv.text(560, 610, "REACTIVOS", 34, mix(BG, GREY, a1))
    cv.text(1350, 610, "PRODUCTOS", 34, mix(BG, GREY, a3))

    a4 = fade(t, 3.6)
    cv.text(560, 720, "Se ROMPEN enlaces", 40, mix(BG, RED, a4), bold=True)
    a5 = fade(t, 4.6)
    cv.text(1350, 720, "Se FORMAN enlaces nuevos", 40, mix(BG, GREEN, a5), bold=True)
    a6 = fade(t, 5.8)
    cv.text(W / 2, 830, "Los átomos no se crean ni se destruyen: solo se reorganizan",
            36, mix(BG, YELLOW, a6))


SIM_INTRO = None
SIM_T_LO = SIM_T_HI = SIM_C_LO = SIM_C_HI = None


def scene_motion(cv, t, D):
    title(cv, t, "Las partículas se mueven y chocan continuamente")
    x0, y0, w, h = 360, 170, 1200, 690
    draw_sim(cv, SIM_INTRO, t, x0, y0, w, h, 26)
    n = count_all(SIM_INTRO, t)
    cv.rect(1600, 420, 1860, 600, fill=PANEL, outline=GRID, width=3, radius=14)
    cv.text(1730, 470, "Choques", 34, GREY)
    cv.text(1730, 540, str(n), 64, WHITE, bold=True)


def scene_conditions(cv, t, D):
    cv.text(W / 2, 220, "¡No todos los choques producen reacción!", 64,
            mix(BG, YELLOW, fade(t, 0.2)), bold=True)
    cv.text(W / 2, 360, "Para que un choque sea EFICAZ se necesita:", 44,
            mix(BG, WHITE, fade(t, 1.4)))
    items = [("1", "Energía suficiente", "(igual o mayor que la energía de activación, Ea)", 2.4),
             ("2", "Orientación adecuada", "(las partículas deben chocar «por el lado correcto»)", 3.6)]
    for k, (num, a, b, t0) in enumerate(items):
        al = fade(t, t0)
        y = 500 + k * 170
        cv.circle(560, y, 42, fill=mix(BG, GREEN, al))
        cv.text(560, y + 2, num, 46, mix(BG, BG, al), bold=True)
        cv.text(630, y - 22, a, 48, mix(BG, WHITE, al), anchor="lm", bold=True)
        cv.text(630, y + 34, b, 32, mix(BG, GREY, al), anchor="lm")


# --- Choque de dos moléculas: tres casos -----------------------------------
CX, CY = 820, 470
R_AT, D_BOND = 45, 95


def energy_meter(cv, t, level, ea=0.6):
    x0, x1, top, bot = 1700, 1780, 250, 740
    cv.text((x0 + x1) / 2, 200, "Energía del choque", 30, GREY, bold=True)
    cv.rect(x0, top, x1, bot, fill=PANEL, outline=GRID, width=3, radius=10)
    lv = level * ramp(t, 0.3, 1.3)
    col = GREEN if level >= ea else ORANGE
    yfill = bot - (bot - top) * lv
    if yfill < bot - 8:
        cv.rect(x0 + 6, yfill, x1 - 6, bot - 6, fill=col, radius=6)
    yea = bot - (bot - top) * ea
    cv.dashed(x0 - 40, yea, x1 + 20, yea, YELLOW, width=4, dash=12, gap=8)
    cv.text(x0 - 50, yea, "Ea", 40, YELLOW, anchor="rm", bold=True)


def approach_x(t, tc, v, x_contact, side):
    """Posición x del centro de una molécula: se acerca a velocidad v hasta
    el choque (t = tc) y después rebota y se frena suavemente."""
    if t <= tc:
        return x_contact - side * v * (tc - t)
    D = 330
    return x_contact - side * D * (1 - math.exp(-(t - tc) * v / D))


def speed_arrows(cv, t, tc, xa, xb, v, y):
    a = 1 - ramp(t, tc - 0.3, tc)
    if a <= 0:
        return
    L = 50 + v * 0.3
    c = mix(BG, WHITE, a)
    cv.arrow(xa - L / 2, y, xa + L / 2, y, c, width=6, head=20)
    cv.arrow(xb + L / 2, y, xb - L / 2, y, c, width=6, head=20)


def result_label(cv, t, t0, ok, line1, line2):
    a = fade(t, t0, 0.5)
    if a <= 0:
        return
    col = GREEN if ok else RED
    w1 = cv.text_width(line1, 54, True)
    x = CX - w1 / 2 + 40
    if ok:
        check_mark(cv, x - 60, 772, 56, mix(BG, col, a), w=11)
    else:
        cross_mark(cv, x - 60, 772, 44, mix(BG, col, a), w=11)
    cv.text(x, 772, line1, 54, mix(BG, col, a), anchor="lm", bold=True)
    cv.text(CX, 848, line2, 36, mix(BG, WHITE, a))


def case_header(cv, t, n, s):
    cv.text(W / 2, 80, f"CASO {n}", 32, mix(BG, GREY, fade(t, 0)), bold=True)
    cv.text(W / 2, 135, s, 50, mix(BG, WHITE, fade(t, 0.1)), bold=True)


def scene_case_low(cv, t, D):
    case_header(cv, t, 1, "Chocan con poca energía")
    energy_meter(cv, t, 0.3)
    v, tc = 110, 3.4
    xc = R_AT
    xa = approach_x(t, tc, v, CX - xc, +1)
    xb = approach_x(t, tc, v, CX + xc, -1)
    if t > tc:
        burst(cv, CX, CY - D_BOND / 2, t - tc, big=False)
        burst(cv, CX, CY + D_BOND / 2, t - tc, big=False)
    diatomic(cv, xa, CY, "A", "A", ang=math.pi / 2, d=D_BOND, r=R_AT)
    diatomic(cv, xb, CY, "B", "B", ang=math.pi / 2, d=D_BOND, r=R_AT)
    speed_arrows(cv, t, tc, xa, xb, v, CY - 140)
    result_label(cv, t, tc + 0.7, False, "Choque NO eficaz",
                 "Energía menor que Ea: los enlaces no se rompen y rebotan")


def scene_case_orient(cv, t, D):
    case_header(cv, t, 2, "Chocan con energía, pero mal orientadas")
    energy_meter(cv, t, 0.85)
    v, tc = 330, 1.8
    xc = R_AT + D_BOND / 2
    xa = approach_x(t, tc, v, CX - xc, +1)
    xb = approach_x(t, tc, v, CX + xc, -1)
    rot = 0.0 if t < tc else 1.3 * (1 - math.exp(-(t - tc) * 1.6))
    if t > tc:
        burst(cv, CX, CY, t - tc, big=False)
    diatomic(cv, xa, CY, "A", "A", ang=-rot, d=D_BOND, r=R_AT)
    diatomic(cv, xb, CY, "B", "B", ang=rot, d=D_BOND, r=R_AT)
    speed_arrows(cv, t, tc, xa, xb, v, CY - 120)
    # indicación de la orientación
    a = fade(t, 0.4, 0.5, t_out=tc - 0.4)
    if a > 0:
        cv.text(CX, CY + 130, "Chocan «de punta»: solo se tocan un A y un B", 34,
                mix(BG, YELLOW, a))
    result_label(cv, t, tc + 0.9, False, "Choque NO eficaz",
                 "Orientación inadecuada: los átomos no pueden reorganizarse")


def scene_case_ok(cv, t, D):
    case_header(cv, t, 3, "Energía suficiente y orientación adecuada")
    energy_meter(cv, t, 0.85)
    v, tc, ttr = 330, 1.8, 1.0
    if t <= tc:
        xa = approach_x(t, tc, v, CX - R_AT, +1)
        xb = approach_x(t, tc, v, CX + R_AT, -1)
        diatomic(cv, xa, CY, "A", "A", ang=math.pi / 2, d=D_BOND, r=R_AT)
        diatomic(cv, xb, CY, "B", "B", ang=math.pi / 2, d=D_BOND, r=R_AT)
        speed_arrows(cv, t, tc, xa, xb, v, CY - 140)
    else:
        p = ease((t - tc) / ttr)
        # destello del complejo activado
        ga = math.exp(-((t - tc - 0.35) / 0.35) ** 2)
        cv.glow(CX, CY, 230, YELLOW, 0.75 * ga)
        # posiciones: del contacto a dos moléculas AB que se separan
        h = D_BOND / 2
        Dm = 240
        s = 0.0 if t < tc + ttr * 0.6 else Dm * (1 - math.exp(-(t - tc - ttr * 0.6) * 1.2))
        ux, uy = 0.8, -0.6
        gap = lerp(R_AT, D_BOND / 2, p)
        top = (CX + ux * s, CY - h + uy * s - 18 * p)
        bot = (CX - ux * s, CY + h - uy * s + 18 * p)
        A1 = (top[0] - gap, top[1])
        B1 = (top[0] + gap, top[1])
        A2 = (bot[0] - gap, bot[1])
        B2 = (bot[0] + gap, bot[1])
        old = 1 - ramp(t, tc + 0.15, tc + 0.6)
        new = ramp(t, tc + 0.45, tc + 0.95)
        # enlaces que se rompen (A–A y B–B): parpadean y desaparecen
        bond(cv, A1, A2, old, color=mix(BOND, RED, ramp(t, tc, tc + 0.2)))
        bond(cv, B1, B2, old, color=mix(BOND, RED, ramp(t, tc, tc + 0.2)))
        bond(cv, A1, B1, new, color=mix(GREEN, BOND, ramp(t, tc + 1.0, tc + 2.0)))
        bond(cv, A2, B2, new, color=mix(GREEN, BOND, ramp(t, tc + 1.0, tc + 2.0)))
        for P, k in ((A1, "A"), (B1, "B"), (A2, "A"), (B2, "B")):
            atom(cv, *P, k, r=R_AT)
        a = fade(t, tc + 0.1, 0.3, t_out=tc + 1.3)
        if a > 0:
            cv.text(CX - 330, CY, "Se rompen A–A y B–B", 32, mix(BG, RED, a), anchor="rm", bold=True)
        a = fade(t, tc + 0.6, 0.3, t_out=tc + 2.4)
        if a > 0:
            cv.text(CX + 330, CY, "Se forman dos A–B", 32, mix(BG, GREEN, a), anchor="lm", bold=True)
    result_label(cv, t, tc + 2.2, True, "Choque EFICAZ: ¡hay reacción!",
                 "A₂ + B₂  →  2 AB")


# --- Diagrama de energía ---------------------------------------------------
ER, EP, HB = 0.30, 0.12, 0.62


def E_curve(x):
    S = 1 / (1 + math.exp(-(x - 0.5) / 0.07))
    return ER + (EP - ER) * S + HB * math.exp(-((x - 0.5) / 0.17) ** 2)


_xs = np.linspace(0, 1, 400)
_es = np.array([E_curve(x) for x in _xs])
X_PEAK = float(_xs[_es.argmax()])
E_PEAK = float(_es.max())
PX0, PX1, PY0, PY1 = 300, 1300, 830, 230


def pmap(x, e):
    return (PX0 + 40 + x * (PX1 - PX0 - 60), PY0 - e * (PY0 - PY1) * 0.95)


def scene_energy(cv, t, D):
    title(cv, t, "La energía de activación (Ea)")
    a_ax = fade(t, 0.2)
    ax = mix(BG, GREY, a_ax)
    cv.arrow(PX0, PY0, PX0, PY1 - 30, ax, width=5, head=20)
    cv.arrow(PX0, PY0, PX1 + 20, PY0, ax, width=5, head=20)
    cv.text(PX0, PY1 - 60, "Energía", 32, ax, anchor="mm", bold=True)
    cv.text((PX0 + PX1) / 2, PY0 + 45, "Avance de la reacción", 32, ax, bold=True)
    # curva que se dibuja progresivamente
    u = ramp(t, 0.6, 2.4)
    if u > 0:
        n = max(2, int(200 * u))
        pts = [pmap(x, E_curve(x)) for x in np.linspace(0.02, 0.02 + 0.96 * u, n)]
        cv.line(pts, WHITE, 7)
    a_lab = fade(t, 2.2)
    xr, yr = pmap(0.1, ER)
    xp, yp = pmap(0.9, EP)
    cv.text(xr, yr - 80, "Reactivos", 34, mix(BG, WHITE, a_lab), bold=True)
    cv.text(xr, yr - 40, "A₂ + B₂", 30, mix(BG, GREY, a_lab))
    cv.text(xp + 40, yp - 120, "Productos", 34, mix(BG, WHITE, a_lab), bold=True)
    cv.text(xp + 40, yp - 80, "2 AB", 30, mix(BG, GREY, a_lab))
    # Ea
    a_ea = fade(t, 3.0)
    if a_ea > 0:
        xpk, ypk = pmap(X_PEAK, E_PEAK)
        _, yer = pmap(0, ER)
        cv.dashed(pmap(0.02, 0)[0], yer, xpk + 60, yer, mix(BG, YELLOW, a_ea), width=3)
        xa = xpk
        cv.arrow(xa, yer, xa, ypk + 14, mix(BG, YELLOW, a_ea), width=6, head=22)
        cv.arrow(xa, ypk + 10, xa, yer - 4, mix(BG, YELLOW, a_ea), width=6, head=22)
        cv.text(xa + 18, yer - (yer - ypk) * 0.3, "Ea", 46, mix(BG, YELLOW, a_ea), anchor="lm", bold=True)
    a_ca = fade(t, 3.8)
    if a_ca > 0:
        xpk, ypk = pmap(X_PEAK, E_PEAK)
        cv.text(xpk, ypk - 75, "Complejo activado", 30, mix(BG, WHITE, a_ca), anchor="mm", bold=True)
    # panel explicativo
    a_p = fade(t, 1.0)
    cv.rect(1380, 250, 1860, 560, fill=mix(BG, PANEL, a_p), outline=mix(BG, GRID, a_p), width=3, radius=16)
    lines = ["Ea: energía mínima que", "deben tener las partículas", "al chocar para que el", "choque sea eficaz."]
    for k, s in enumerate(lines):
        cv.text(1410, 300 + k * 50, s, 32, mix(BG, WHITE, a_p), anchor="lm")
    cv.text(1410, 510, "Es como una colina", 32, mix(BG, YELLOW, fade(t, 3.4)), anchor="lm", bold=True)

    # bolitas que intentan superar la barrera
    def ball(x, col, a):
        bx, by = pmap(x, E_curve(x))
        cv.glow(bx, by - 30, 60, col, 0.6 * a)
        cv.circle(bx, by - 28, 24, fill=mix(BG, col, a))
        cv.circle(bx - 7, by - 36, 7, fill=mix(BG, tint(col, 0.5), a))

    t1a, t1b = 5.0, 8.4
    if t1a <= t <= t1b + 0.5:
        u = clamp((t - t1a) / (t1b - t1a))
        x = 0.08 + 0.28 * math.sin(math.pi * u)
        ball(x, ORANGE, fade(t, t1a, 0.3, t_out=t1b, dur_out=0.4))
    a = fade(t, t1a, 0.4, t_out=t1b + 0.2)
    if a > 0:
        cv.text(1400, 650, "Energía < Ea", 36, mix(BG, ORANGE, a), anchor="lm", bold=True)
        cv.text(1400, 700, "no llega a la cima:", 32, mix(BG, WHITE, a), anchor="lm")
        cv.text(1400, 745, "vuelve atrás (no reacciona)", 32, mix(BG, WHITE, a), anchor="lm")
    t2a, t2b = 9.0, 12.4
    if t >= t2a:
        u = (t - t2a) / (t2b - t2a)
        x = 0.08 + 0.84 * ease(u)
        ball(x, GREEN, fade(t, t2a, 0.3))
        if 0 < u - 0.45 < 0.5:
            pass
    a = fade(t, t2a + 0.6, 0.4)
    if a > 0:
        cv.text(1400, 650, "Energía ≥ Ea", 36, mix(BG, GREEN, a), anchor="lm", bold=True)
        cv.text(1400, 700, "supera la barrera:", 32, mix(BG, WHITE, a), anchor="lm")
        cv.text(1400, 745, "¡se forman los productos!", 32, mix(BG, WHITE, a), anchor="lm")


# --- Factores: temperatura y concentración --------------------------------
BX = [(120, 260), (1020, 260)]
BW, BH, BR = 780, 560, 17


def legend(cv, y):
    items = [("A", "A"), ("B", "B"), ("P", "AB (producto)")]
    x = W / 2 - 300
    for k, lab in items:
        atom(cv, x, y, k, r=16, label="")
        cv.text(x + 28, y, lab, 30, GREY, anchor="lm")
        x += 70 + cv.text_width(lab, 30) + 30


def two_boxes(cv, t, sims, labels, colors, header):
    title(cv, t, header, y=70)
    legend(cv, 140)
    for (x0, y0), sim, lab, col in zip(BX, sims, labels, colors):
        cv.text(x0 + BW / 2, y0 - 40, lab, 38, col, bold=True)
        draw_sim(cv, sim, t, x0, y0, BW, BH, BR, show_minor=True)
        n = count_eff(sim, t)
        cv.text(x0 + BW / 2, y0 + BH + 55, f"Choques eficaces: {n}", 38, WHITE, bold=True)


def scene_temperature(cv, t, D):
    two_boxes(cv, t, (SIM_T_LO, SIM_T_HI), ("Temperatura baja", "Temperatura alta"),
              (COL["B"], ORANGE), "Factor 1: la temperatura")


def scene_concentration(cv, t, D):
    two_boxes(cv, t, (SIM_C_LO, SIM_C_HI), ("Concentración baja", "Concentración alta"),
              (GREY, YELLOW), "Factor 2: la concentración")


def scene_summary(cv, t, D):
    title(cv, t, "En resumen", y=110, size=70, color=YELLOW)
    cv.text(W / 2, 230, "Una reacción química ocurre cuando las partículas:", 44,
            mix(BG, WHITE, fade(t, 0.5)))
    items = [("Chocan entre sí", 1.5),
             ("con energía suficiente (≥ Ea)", 2.7),
             ("y con la orientación adecuada", 3.9)]
    for k, (s, t0) in enumerate(items):
        a = fade(t, t0)
        y = 350 + k * 100
        check_mark(cv, 560, y, 50, mix(BG, GREEN, a), w=10)
        cv.text(620, y, s, 50, mix(BG, WHITE, a), anchor="lm", bold=True)
    a = fade(t, 5.6)
    cv.rect(260, 680, 1660, 860, fill=mix(BG, PANEL, a), outline=mix(BG, GRID, a), width=3, radius=18)
    cv.text(W / 2, 735, "↑ Temperatura   o   ↑ Concentración", 44, mix(BG, ORANGE, a), bold=True)
    cv.text(W / 2, 805, "→ más choques eficaces → reacción más rápida", 42, mix(BG, WHITE, a))


def scene_end(cv, t, D):
    cv.text(W / 2, H / 2 - 30, "Teoría de colisiones", 80, mix(BG, WHITE, fade(t, 0.1, 0.6, D - 0.8, 0.6)), bold=True)
    cv.text(W / 2, H / 2 + 50, "Física y Química", 40, mix(BG, GREY, fade(t, 0.4, 0.6, D - 0.8, 0.6)))


# --------------------------------------------------------------------------
# Guion: escenas, duración y narración (subtítulos)
# --------------------------------------------------------------------------
SCENES = [
    (6.0, scene_title, [
        (1.5, "¿Qué tiene que pasar para que ocurra una reacción química?")]),
    (10.0, scene_what_is, [
        (0.3, "En una reacción química los átomos se reorganizan."),
        (3.4, "Se rompen los enlaces de los reactivos y se forman enlaces nuevos en los productos."),
        (7.2, "Para eso, las partículas tienen que encontrarse.")]),
    (10.0, scene_motion, [
        (0.3, "Las partículas (átomos, moléculas o iones) están en continuo movimiento"),
        (4.0, "y chocan entre sí millones de veces por segundo."),
        (6.8, "Para reaccionar, lo primero es que choquen.")]),
    (7.0, scene_conditions, [
        (0.3, "Pero no todos los choques producen una reacción."),
        (3.0, "Para que un choque sea eficaz hacen falta dos condiciones.")]),
    (10.0, scene_case_low, [
        (0.3, "Imagina dos moléculas, A₂ y B₂, que se acercan despacio."),
        (4.2, "Si chocan con poca energía, los enlaces no llegan a romperse:"),
        (7.0, "rebotan y no hay reacción.")]),
    (10.0, scene_case_orient, [
        (0.3, "Ahora chocan rápido, con energía suficiente…"),
        (3.0, "pero de punta: la orientación no es la adecuada."),
        (6.0, "Rebotan y tampoco hay reacción.")]),
    (11.0, scene_case_ok, [
        (0.3, "Con energía suficiente y la orientación adecuada…"),
        (2.0, "se rompen los enlaces A–A y B–B y se forman dos enlaces A–B."),
        (5.5, "¡El choque es eficaz y se forma el producto!")]),
    (14.5, scene_energy, [
        (0.3, "La energía mínima que necesita el choque se llama energía de activación, Ea."),
        (4.8, "Es como una colina: si las partículas no tienen energía suficiente, no llegan a la cima y vuelven atrás."),
        (9.0, "Si la energía es igual o mayor que Ea, superan la barrera y se forman los productos.")]),
    (15.0, scene_temperature, [
        (0.3, "Al aumentar la temperatura, las partículas se mueven más rápido."),
        (5.0, "Chocan más veces y con más energía: hay más choques eficaces"),
        (9.5, "y la reacción es más rápida. (Las moléculas moradas son el producto AB).")]),
    (13.0, scene_concentration, [
        (0.3, "Al aumentar la concentración hay más partículas en el mismo volumen."),
        (5.5, "Hay más choques por segundo, más choques eficaces, y la reacción se acelera.")]),
    (12.0, scene_summary, [
        (0.3, "En resumen: una reacción química ocurre cuando las partículas chocan"),
        (3.0, "con energía suficiente y con la orientación adecuada."),
        (6.0, "Más temperatura o más concentración significan más choques eficaces y una reacción más rápida.")]),
    (4.0, scene_end, []),
]

STARTS = []
_acc = 0.0
for _d, _f, _c in SCENES:
    STARTS.append(_acc)
    _acc += _d
TOTAL = _acc


def captions():
    out = []
    for (d, _, caps), s in zip(SCENES, STARTS):
        for k, (t0, txt) in enumerate(caps):
            t1 = caps[k + 1][0] if k + 1 < len(caps) else d - 0.2
            out.append((s + t0, s + t1, txt))
    return out


CAPS = captions()


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
            # fundido entre escenas
            break
    draw_caption(cv, T)
    img = cv.final()
    # fundido a negro breve al inicio y al final de cada escena
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


def build_sims():
    global SIM_INTRO, SIM_T_LO, SIM_T_HI, SIM_C_LO, SIM_C_HI
    d = dict((f.__name__, dur) for dur, f, _ in SCENES)
    SIM_INTRO = simulate(9, 9, 1200, 690, 26, 150, d["scene_motion"], seed=3)
    thr, p = 300, 0.5
    SIM_T_LO = simulate(14, 14, BW, BH, BR, 80, d["scene_temperature"], seed=11, thr=thr, p_orient=p, react=True)
    SIM_T_HI = simulate(14, 14, BW, BH, BR, 190, d["scene_temperature"], seed=11, thr=thr, p_orient=p, react=True)
    SIM_C_LO = simulate(5, 5, BW, BH, BR, 160, d["scene_concentration"], seed=5, thr=thr, p_orient=p, react=True)
    SIM_C_HI = simulate(20, 20, BW, BH, BR, 160, d["scene_concentration"], seed=5, thr=thr, p_orient=p, react=True)


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
    global OUT_SCALE
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", type=float, nargs="*", help="segundos a exportar como PNG")
    ap.add_argument("--hd720", action="store_true")
    ap.add_argument("-o", "--output", default=os.path.join(HERE, "teoria_colisiones.mp4"))
    args = ap.parse_args()
    if args.hd720:
        OUT_SCALE = 2 / 3

    build_sims()
    print(f"Duración total: {TOTAL:.1f} s")
    for name, sim in (("T baja", SIM_T_LO), ("T alta", SIM_T_HI),
                      ("C baja", SIM_C_LO), ("C alta", SIM_C_HI)):
        print(f"  choques eficaces {name}: {count_eff(sim, 1e9)} / choques: {len(sim[1])}")

    if args.preview is not None:
        for s in args.preview:
            p = os.path.join(HERE, f"preview_{s:05.1f}.png")
            render(s).save(p)
            print("guardado", p)
        return

    srt = os.path.splitext(args.output)[0] + ".srt"
    write_srt(srt)
    print("subtítulos:", srt)

    nfr = int(TOTAL * FPS)
    ow, oh = int(W * OUT_SCALE), int(H * OUT_SCALE)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{ow}x{oh}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", args.output]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    ctx = mp.get_context("fork")
    with ctx.Pool(os.cpu_count()) as pool:
        for k, buf in enumerate(pool.imap(render_frame, range(nfr), chunksize=4)):
            proc.stdin.write(buf)
            if k % 150 == 0:
                print(f"  fotograma {k}/{nfr}", flush=True)
    proc.stdin.close()
    proc.wait()
    print("vídeo:", args.output)


if __name__ == "__main__":
    main()
