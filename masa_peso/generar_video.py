#!/usr/bin/env python3
"""
Vídeo vertical (1080x1920): «Peso y masa en un minuto», con una manzana.

Uso:
    python3 generar_video.py               # vídeo + subtítulos .srt
    python3 generar_video.py --preview 20  # PNG del segundo 20
"""

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "comun"))
from reel import (  # noqa: E402
    Reel, W, INK, PAPER, ORANGE, BLUE, GREY, LIGHT, YELLOW, GREEN, SS, mix,
    pop, ramp, text_w, formula, fit, headline, highlight, sticker, card, chip, check,
)

RED = (226, 58, 44)
C_P, C_M, C_G = ORANGE, BLUE, GREEN


# --------------------------------------------------------------------------
# Ilustraciones
# --------------------------------------------------------------------------
def apple(cv, x, y, r, s=1.0):
    """Manzana centrada en (x, y)."""
    r *= s
    if r < 3:
        return
    w = max(4, r * 0.085)
    d = cv.d
    d.ellipse([(x - r + 7) * SS, (y - r * 0.9 + 9) * SS, (x + r + 7) * SS, (y + r * 0.9 + 9) * SS], fill=INK)
    d.ellipse([(x - r) * SS, (y - r * 0.9) * SS, (x + r) * SS, (y + r * 0.9) * SS], fill=RED, outline=INK,
              width=int(w * SS))
    cv.circle(x - r * 0.42, y - r * 0.36, r * 0.15, fill=mix(RED, PAPER, 0.6), width=0)
    cv.line([(x, y - r * 0.82), (x + r * 0.1, y - r * 1.2)], INK, w * 1.2)
    lx, ly = x + r * 0.42, y - r * 1.12
    pts = [(lx + r * 0.36 * math.cos(a) * math.cos(-0.5) - r * 0.16 * math.sin(a) * math.sin(-0.5),
            ly + r * 0.36 * math.cos(a) * math.sin(-0.5) + r * 0.16 * math.sin(a) * math.cos(-0.5))
           for a in [i * math.pi / 10 for i in range(20)]]
    cv.poly(pts, GREEN, INK, w * 0.8)


def earth(cv, x, y, r):
    cv.circle(x + 10, y + 12, r, fill=INK, width=0)
    cv.circle(x, y, r, fill=BLUE)
    for dx, dy, rr in ((-0.35, -0.3, 0.3), (-0.12, -0.5, 0.22), (0.38, 0.1, 0.28), (0.2, 0.42, 0.2), (-0.45, 0.3, 0.16)):
        cv.circle(x + dx * r, y + dy * r, rr * r, fill=GREEN, width=0)
    cv.circle(x, y, r, fill=None)


def moon(cv, x, y, r):
    cv.circle(x + 10, y + 12, r, fill=INK, width=0)
    cv.circle(x, y, r, fill=LIGHT)
    for dx, dy, rr in ((-0.35, -0.25, 0.2), (0.3, -0.4, 0.13), (0.35, 0.25, 0.24), (-0.2, 0.45, 0.14), (-0.55, 0.2, 0.09)):
        cv.circle(x + dx * r, y + dy * r, rr * r, fill=GREY, width=5)


def fall(t, period, frac):
    """0 (arriba) -> 1 (apoyada). Cae durante `frac` del periodo y espera."""
    u = (t % period) / period
    return (u / frac) ** 2 if u < frac else 1.0


def planet_apple(cv, t, kind, x, y, r, drop=260, arrow=None, s=1.0, r_ap=58):
    """Planeta con la manzana cayendo una y otra vez encima."""
    if s < 0.5:
        return
    (earth if kind == "tierra" else moon)(cv, x, y, r)
    f = fall(t, 1.5, 0.3) if kind == "tierra" else fall(t, 2.8, 0.75)
    ya = y - r - r_ap * 0.78 - drop * (1 - f)
    apple(cv, x, ya, r_ap)
    if arrow:                                  # flecha del peso, junto al planeta
        ax = x + r * 0.78 + 62
        cv.arrow(ax, y - r - 215, ax, y - r - 215 + arrow, ORANGE, 14, 44)


def wob(t, k=0.0, a=6):
    return a * math.sin(t * 3 + k)


# --------------------------------------------------------------------------
# Escenas
# --------------------------------------------------------------------------
def s_hook(cv, t, D):
    headline(cv, t, 330, [[("¿Peso", True)], [("o masa?", False)]], 150)
    u = max(0.0, t - 0.5)                      # la manzana cae y rebota
    b = abs(math.cos(u * 4.2)) * math.exp(-u * 0.9)
    if t > 0.5:
        cv.line([(300, 1232), (780, 1232)], INK, 10)
        apple(cv, 540, 1090 - 480 * b, 150)
    sticker(cv, 810, 700 + wob(t), "¿diferencia?", 50, 7, PAPER, pop(t, 1.2))
    sticker(cv, 290, 770 + wob(t, 2), "en 1 minuto", 64, -8, YELLOW, pop(t, 3.6))


def s_masa(cv, t, D):
    headline(cv, t, 340, [[("La ", False), ("masa", True)]], 130)
    big = pop(t, 0.2) * (1 - ramp(t, 1.8, 2.1))
    if big > 0.02:
        apple(cv, 540, 830 + wob(t, 0, 14), 170, min(big, 1.05))
    if pop(t, 1.9) > 0.5:
        earth(cv, 280, 940, 150)
        apple(cv, 280, 940 - 150 - 46 + wob(t, 0, 5), 60)
        chip(cv, 280, 1140, "TIERRA", 34, BLUE, PAPER, anchor="c")
    if pop(t, 2.3) > 0.5:
        moon(cv, 800, 960, 110)
        apple(cv, 800, 960 - 110 - 46 + wob(t, 1.5, 5), 60)
        chip(cv, 800, 1140, "LUNA", 34, GREY, PAPER, anchor="c")
    sticker(cv, 540, 780, "=", 130, 0, YELLOW, pop(t, 3.0))
    sticker(cv, 280, 610 + wob(t, 1), "0,2 kg", 54, -6, PAPER, pop(t, 6.0))
    sticker(cv, 800, 640 + wob(t, 2), "0,2 kg", 54, 6, PAPER, pop(t, 6.3))
    sticker(cv, 540, 1245, [("MASA · en kg", PAPER)], 62, -3, BLUE, pop(t, 6.6))


def s_peso(cv, t, D):
    headline(cv, t, 340, [[("El ", False), ("peso", True)]], 130)
    if pop(t, 0.3) > 0.5:
        planet_apple(cv, t, "tierra", 540, 1100, 200, drop=300, r_ap=80)
        pulse = 1 + 0.08 * math.sin(t * 6)
        u = ramp(t, 0.9, 1.5)
        if u > 0:
            cv.arrow(760, 560, 760, 560 + 250 * u * pulse, ORANGE, 20, 60)
    sticker(cv, 890, 640 + wob(t), "P", 96, 6, ORANGE, pop(t, 1.4))
    sticker(cv, 260, 640 + wob(t, 2), "es una fuerza", 48, -7, PAPER, pop(t, 2.2))
    sticker(cv, 240, 775 + wob(t, 1), "newtons (N)", 46, 5, YELLOW, pop(t, 5.2))


def s_formula(cv, t, D):
    headline(cv, t, 340, [[("La ", False), ("fórmula", True)]], 120)
    s = pop(t, 0.3)
    card(cv, 60, 500, 1010, 800, scale=s)
    if s > 0.85:
        tt = [0.6, 0.6, 1.5, 1.5, 2.4]
        parts = [("P", C_P), (" = ", INK), ("m", C_M), (" · ", INK), ("g", C_G)]
        shown = [(txt, col if t >= t0 else PAPER) for (txt, col), t0 in zip(parts, tt)]
        formula(cv, W / 2, 650, shown, fit(parts, 240, 840))
    for k, (t0, sym, col, name, unit) in enumerate(((0.6, "P", C_P, "peso", "N"), (1.5, "m", C_M, "masa", "kg"),
                                                    (2.4, "g", C_G, "gravedad", "N/kg"))):
        sc = pop(t, t0 + 0.2)
        x0 = 60 + k * 322
        card(cv, x0, 870, x0 + 306, 1150, scale=sc, shadow=10)
        if sc > 0.85:
            cv.circle(x0 + 153, 945, 50, fill=col, width=7)
            cv.text(x0 + 153, 943, sym, 66, PAPER)
            cv.text(x0 + 153, 1045, name, min(46, 46 * 270 / text_w(name, 46)), INK)
            cv.text(x0 + 153, 1105, unit, 38, GREY, "bold")
    apple(cv, 540, 1255 + wob(t, 0, 8), 46, pop(t, 3.0))


def calc_scene(cv, t, kind, g_txt, calc, res, arrow):
    s = pop(t, 0.3)
    if kind == "tierra":
        planet_apple(cv, t, kind, 290, 830, 150, arrow=arrow, s=s)
    else:
        planet_apple(cv, t, kind, 290, 850, 115, arrow=arrow, s=s)
    sticker(cv, 770, 580 + wob(t), g_txt, 64, 5, YELLOW, pop(t, 0.8))
    sticker(cv, 770, 740 + wob(t, 2), "m = 0,2 kg", 54, -5, PAPER, pop(t, 3.2))
    sc = pop(t, 3.6)
    card(cv, 60, 990, 1010, 1300, scale=sc)
    if sc > 0.85:
        formula(cv, W / 2, 1070, calc, 84)
        s3 = pop(t, 4.6)
        if s3 > 0.02:
            sz = 112 * min(s3, 1.05)
            ww = text_w(res, sz)
            highlight(cv, W / 2 - ww / 2, 1205 - sz * 0.5, W / 2 + ww / 2, 1205 + sz * 0.46)
            cv.text(W / 2, 1205, res, sz, INK)


def s_tierra(cv, t, D):
    headline(cv, t, 340, [[("En la ", False), ("Tierra", True)]], 112)
    calc_scene(cv, t, "tierra", "g = 9,8", [("P", C_P), (" = ", INK), ("0,2", C_M), (" · ", INK), ("9,8", C_G)],
               "P = 1,96 N", 190)


def s_luna(cv, t, D):
    headline(cv, t, 340, [[("En la ", False), ("Luna", True)]], 112)
    calc_scene(cv, t, "luna", "g = 1,6", [("P", C_P), (" = ", INK), ("0,2", C_M), (" · ", INK), ("1,6", C_G)],
               "P = 0,32 N", 60)


def s_misma(cv, t, D):
    headline(cv, t, 320, [[("Misma masa,", False)], [("distinto peso", True)]], 100)
    planet_apple(cv, t, "tierra", 280, 940, 150, drop=200, arrow=190, s=pop(t, 0.2))
    planet_apple(cv, t, "luna", 800, 965, 110, drop=200, arrow=60, s=pop(t, 0.5))
    sticker(cv, 280, 1178, "0,2 kg", 50, -4, PAPER, pop(t, 0.9))
    sticker(cv, 800, 1178, "0,2 kg", 50, 4, PAPER, pop(t, 1.1))
    sticker(cv, 280, 1288, "1,96 N", 58, 3, ORANGE, pop(t, 1.5))
    sticker(cv, 800, 1288, "0,32 N", 58, -3, ORANGE, pop(t, 1.8))


def s_resumen(cv, t, D):
    headline(cv, t, 340, [[("Recuerda", True)]], 130)
    for k, (t0, txt, unit, col) in enumerate(((0.5, "La masa no cambia", "kg", BLUE),
                                              (1.8, "El peso sí cambia", "N", ORANGE))):
        s = pop(t, t0)
        y0 = 500 + k * 225
        card(cv, 60, y0, 1010, y0 + 190, scale=s)
        if s > 0.85:
            check(cv, 150, y0 + 95, 46, col)
            cv.text(235, y0 + 95, txt, min(54, 54 * 600 / text_w(txt, 54)), INK, "black", "lm")
            cv.circle(915, y0 + 95, 58, fill=col, width=7)
            cv.text(915, y0 + 93, unit, 50, PAPER)
    s = pop(t, 3.5)
    card(cv, 60, 960, 1010, 1270, fill=YELLOW, scale=s)
    if s > 0.85:
        parts = [("P", C_P), (" = ", INK), ("m", C_M), (" · ", INK), ("g", C_G)]
        formula(cv, W / 2, 1115, parts, fit(parts, 200, 840))


def s_fin(cv, t, D):
    s = pop(t, 0.1)
    if s > 0.02:
        sz = 120 * min(s, 1.05)
        ww = text_w("@quantafyq", sz)
        highlight(cv, W / 2 - ww / 2, 860 - sz * 0.5, W / 2 + ww / 2, 860 + sz * 0.46, grow=ramp(t, 0.3, 0.7))
        cv.text(W / 2, 860, "@quantafyq", sz, INK)
    if pop(t, 0.6) > 0.02:
        cv.text(W / 2, 1010, "Física y Química", 60, INK, "bold")
    apple(cv, 540, 1220 + wob(t, 0, 10), 70, pop(t, 0.8))


# --------------------------------------------------------------------------
# Guion: (duración, escena, [(segundo, subtítulo, texto hablado opcional)])
# --------------------------------------------------------------------------
SCENES = [
    (5.5, s_hook, [
        (0.3, "¿Sabes cuál es la diferencia entre peso y masa?"),
        (3.6, "Te lo cuento en un minuto.")]),
    (9.5, s_masa, [
        (0.3, "Mira esta manzana."),
        (1.8, "La cantidad de manzana es la misma en la Tierra que en la Luna."),
        (6.0, "Eso es la masa, y se mide en kilogramos.")]),
    (7.5, s_peso, [
        (0.3, "El peso es otra cosa: es la fuerza con la que el planeta tira de la manzana."),
        (5.2, "Se mide en newtons.", "Se mide en niutons.")]),
    (4.5, s_formula, [
        (0.3, "Se calcula así: P = m · g. Peso es igual a masa por gravedad.",
         "Se calcula así: peso es igual a masa por gravedad.")]),
    (7.5, s_tierra, [
        (0.3, "En la Tierra, la gravedad vale 9,8.", "En la Tierra, la gravedad vale nueve coma ocho."),
        (3.2, "Una manzana de 0,2 kilos pesa 1,96 newtons.",
         "Una manzana de cero coma dos kilos pesa uno coma noventa y seis niutons.")]),
    (7.5, s_luna, [
        (0.3, "En la Luna, la gravedad es solo 1,6.", "En la Luna, la gravedad es solo uno coma seis."),
        (3.2, "La misma manzana pesa 0,32 newtons.",
         "La misma manzana pesa cero coma treinta y dos niutons.")]),
    (3.5, s_misma, [
        (0.3, "Misma masa, distinto peso.")]),
    (6.0, s_resumen, [
        (0.3, "Recuerda: la masa no cambia; el peso, sí."),
        (3.5, "Peso es igual a masa por gravedad.")]),
    (2.5, s_fin, []),
]

VIDEO = Reel(SCENES, HERE, "masa_peso.mp4")
CAPS, TOTAL = VIDEO.caps, VIDEO.total


def barra(cv, T, total):
    """Barra de tiempo: «te lo cuento en un minuto»."""
    x0, x1, y = 290, 790, 208
    cv.rect(x0, y - 9, x1, y + 9, fill=PAPER, width=5, radius=9)
    u = min(1.0, T / total)
    if u > 0.04:
        cv.rect(x0, y - 9, x0 + (x1 - x0) * u, y + 9, fill=ORANGE, width=5, radius=9)


VIDEO.overlay = barra

if __name__ == "__main__":
    VIDEO.main()
