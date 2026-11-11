#!/usr/bin/env python3
"""
Vídeo vertical (1080x1920): «Masa y peso» — diferencias y fórmula P = m · g.

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
    Reel, W, INK, PAPER, ORANGE, BLUE, GREY, LIGHT, YELLOW, GREEN,
    pop, ramp, ease, text_w, formula, fit, headline, highlight, sticker, card, chip, check, countdown,
)

SKIN = (242, 196, 160)
DARK = (58, 56, 68)
C_P, C_M, C_G = ORANGE, BLUE, GREEN


# --------------------------------------------------------------------------
# Ilustraciones
# --------------------------------------------------------------------------
def person(cv, x, y, s=1.0, shirt=BLUE):
    """Personaje con los pies en (x, y)."""
    cv.rect(x - 46 * s, y - 95 * s, x - 6 * s, y, fill=DARK, width=6, radius=10 * s)
    cv.rect(x + 6 * s, y - 95 * s, x + 46 * s, y, fill=DARK, width=6, radius=10 * s)
    cv.rect(x - 82 * s, y - 215 * s, x - 52 * s, y - 105 * s, fill=shirt, width=6, radius=14 * s)
    cv.rect(x + 52 * s, y - 215 * s, x + 82 * s, y - 105 * s, fill=shirt, width=6, radius=14 * s)
    cv.rect(x - 58 * s, y - 225 * s, x + 58 * s, y - 80 * s, fill=shirt, width=7, radius=26 * s)
    cv.circle(x, y - 275 * s, 56 * s, fill=SKIN, width=7)
    for sx in (-1, 1):
        cv.circle(x + sx * 20 * s, y - 282 * s, 7 * s, fill=INK, width=0)
    cv.line([(x - 18 * s, y - 255 * s), (x, y - 247 * s), (x + 18 * s, y - 255 * s)], INK, 6 * s)


def bascula(cv, x, y, txt):
    cv.rect(x - 190, y, x + 190, y + 84, fill=LIGHT, width=7, radius=24)
    cv.rect(x - 100, y + 16, x + 100, y + 68, fill=INK, width=0, radius=10)
    cv.text(x, y + 43, txt, 38, YELLOW)


def dinamometro(cv, x, y, txt, stretch=1.0):
    cv.circle(x, y, 20, fill=None, width=8)
    cv.rect(x - 34, y + 20, x + 34, y + 210, fill=PAPER, width=7, radius=14)
    for k in range(6):
        cv.line([(x - 34, y + 50 + k * 26), (x - 12, y + 50 + k * 26)], INK, 4)
    ind = y + 60 + 90 * stretch
    cv.line([(x - 6, ind), (x + 30, ind)], ORANGE, 8)
    cv.line([(x, y + 210), (x, y + 240 + 30 * stretch)], INK, 7)
    by = y + 240 + 30 * stretch
    cv.rect(x - 46, by, x + 46, by + 80, fill=ORANGE, width=7, radius=12)
    sticker(cv, x + 200, y + 70, txt, 38, 6, YELLOW)


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


def bullets(cv, t, items, y0, h=118, gap=18, color=GREEN):
    for k, (t0, txt) in enumerate(items):
        s = pop(t, t0)
        y = y0 + k * (h + gap)
        card(cv, 60, y, 1010, y + h, scale=s, shadow=10)
        if s > 0.85:
            check(cv, 132, y + h / 2, 34, color)
            cv.text(200, y + h / 2, txt, min(44, 44 * 780 / text_w(txt, 44)), INK, "black", "lm")


def big_formula(cv, y, size, s=1.0):
    parts = [("P", C_P), (" = ", INK), ("m", C_M), (" · ", INK), ("g", C_G)]
    return formula(cv, W / 2, y, parts, fit(parts, size, 840) * min(s, 1.05))


# --------------------------------------------------------------------------
# Escenas
# --------------------------------------------------------------------------
def s_hook(cv, t, D):
    if t < 4.5:
        headline(cv, t, 330, [[("¿Cuánto", False)], [("pesas?", True)]], 120)
    else:
        headline(cv, t, 330, [[("Eso es tu", False)], [("masa", True)]], 120, t0=4.5)
    s = pop(t, 0.8)
    if s > 0.5:
        bascula(cv, 540, 1100, "50 kg")
        person(cv, 540, 1100, 1.25)
    sticker(cv, 830, 760, "«50 kilos»", 54, 7, PAPER, pop(t, 2.2))
    sticker(cv, 290, 640, "¡no es tu peso!", 50, -7, YELLOW, pop(t, 5.2))


def s_masa(cv, t, D):
    headline(cv, t, 340, [[("La ", False), ("masa", True)]], 120)
    s = pop(t, 0.7)
    if s > 0.5:
        bascula(cv, 330, 800, "50 kg")
        person(cv, 330, 800, 0.85)
    sticker(cv, 760, 610, [("m", PAPER)], 120, -6, BLUE, pop(t, 1.2))
    sticker(cv, 760, 770, "kilogramos (kg)", 44, 5, PAPER, pop(t, 4.0))
    bullets(cv, t, [(1.0, "Cantidad de materia"), (4.0, "Se mide con una balanza"),
                    (7.5, "Es la misma en cualquier lugar")], 910)


def s_peso(cv, t, D):
    headline(cv, t, 340, [[("El ", False), ("peso", True)]], 120)
    s = pop(t, 0.7)
    if s > 0.5:
        earth(cv, 300, 850, 130)
        person(cv, 300, 722, 0.6)
        u = ramp(t, 1.4, 2.2)
        if u > 0:
            cv.arrow(430, 560, 430, 560 + 150 * u, ORANGE, 14, 44)
        sticker(cv, 530, 620, "P", 84, 6, ORANGE, pop(t, 2.0))
    if t > 4.5:
        dinamometro(cv, 650, 520, "newtons (N)", ease((t - 4.7) / 0.8))
    bullets(cv, t, [(1.0, "Fuerza con que te atrae la Tierra"), (4.5, "Se mide con un dinamómetro"),
                    (8.5, "Cambia según dónde estés")], 950, color=ORANGE)


def s_formula(cv, t, D):
    headline(cv, t, 340, [[("La ", False), ("fórmula", True)]], 120)
    s = pop(t, 0.8)
    if s > 0.02:
        card(cv, 60, 480, 1010, 760, fill=PAPER, scale=min(s, 1.0))
        big_formula(cv, 620, 230, s)
    rows = [(4.0, "P", C_P, "peso", "newtons (N)"),
            (6.0, "m", C_M, "masa", "kilogramos (kg)"),
            (8.5, "g", C_G, "gravedad", "en la Tierra: 9,8 N/kg")]
    for k, (t0, sym, col, name, unit) in enumerate(rows):
        sc = pop(t, t0)
        y = 820 + k * 158
        card(cv, 60, y, 1010, y + 136, scale=sc, shadow=10)
        if sc > 0.85:
            cv.circle(140, y + 68, 48, fill=col, width=7)
            cv.text(140, y + 66, sym, 64, PAPER)
            cv.text(220, y + 44, name, 50, INK, "black", "lm")
            cv.text(220, y + 98, unit, 36, GREY, "bold", "lm")


def planeta(cv, t, kind, g_txt, p_txt, calc, arrow_len, jump):
    """Escena de cálculo en un planeta."""
    s = pop(t, 0.7)
    if s > 0.5:
        (earth if kind == "tierra" else moon)(cv, 290, 800, 140)
        dy = jump * abs(math.sin(t * (2.2 if kind == "luna" else 5.0)))
        person(cv, 290, 662 - dy, 0.55)
        u = ramp(t, 1.4, 2.0)
        if u > 0:
            cv.arrow(410, 520, 410, 520 + arrow_len * u, ORANGE, 14, 44)
            cv.text(455, 520 + arrow_len / 2, "P", 54, ORANGE, "black", "lm")
    sticker(cv, 760, 560, "m = 50 kg", 54, -5, PAPER, pop(t, 1.0))
    sticker(cv, 760, 700, g_txt, 54, 5, YELLOW, pop(t, 2.0))
    sc = pop(t, 3.6)
    card(cv, 60, 960, 1010, 1300, scale=sc)
    if sc > 0.85:
        formula(cv, W / 2, 1030, [("P", C_P), (" = ", INK), ("m", C_M), (" · ", INK), ("g", C_G)], 72)
        s2 = pop(t, 4.2)
        if s2 > 0.02:
            formula(cv, W / 2, 1125, calc, 72 * min(s2, 1.05))
        s3 = pop(t, 8.0 if kind == "tierra" else 5.5)
        if s3 > 0.02:
            sz = 96 * min(s3, 1.05)
            ww = text_w(p_txt, sz)
            highlight(cv, W / 2 - ww / 2, 1232 - sz * 0.5, W / 2 + ww / 2, 1232 + sz * 0.46)
            cv.text(W / 2, 1232, p_txt, sz, INK)


def s_tierra(cv, t, D):
    headline(cv, t, 340, [[("En la ", False), ("Tierra", True)]], 112)
    planeta(cv, t, "tierra", "g = 9,8 N/kg", "P = 490 N",
            [("P", C_P), (" = ", INK), ("50", C_M), (" · ", INK), ("9,8", C_G)], 170, 6)


def s_luna(cv, t, D):
    headline(cv, t, 340, [[("En la ", False), ("Luna", True)]], 112)
    planeta(cv, t, "luna", "g = 1,6 N/kg", "P = 80 N",
            [("P", C_P), (" = ", INK), ("50", C_M), (" · ", INK), ("1,6", C_G)], 60, 70 if t > 10 else 0)


def s_compara(cv, t, D):
    headline(cv, t, 340, [[("No son ", False), ("lo mismo", True)]], 104)
    sticker(cv, 292, 520, [("MASA", PAPER)], 62, -4, BLUE, pop(t, 0.8))
    sticker(cv, 782, 520, "PESO", 62, 4, ORANGE, pop(t, 1.1))
    rows = [("materia", "fuerza"), ("kilogramos (kg)", "newtons (N)"), ("balanza", "dinamómetro"),
            ("no cambia", "sí cambia")]
    for k, (a, b) in enumerate(rows):
        y = 620 + k * 160
        for x0, x1, txt, t0 in ((60, 520, a, 2.0 + 0.8 * k), (560, 1010, b, 6.0 + 0.8 * k)):
            sc = pop(t, t0)
            card(cv, x0, y, x1, y + 130, scale=sc, shadow=10)
            if sc > 0.85:
                cv.text((x0 + x1) / 2, y + 65, txt, min(46, 46 * 400 / text_w(txt, 46)), INK)


def s_turno(cv, t, D):
    sticker(cv, W / 2, 320, "TU TURNO", 84, -5, ORANGE, pop(t, 0.1))
    s = pop(t, 0.5)
    if s > 0.02:
        cv.text(W / 2, 500, "Una mochila de 5 kg", 64, INK, "black")
        cv.text(W / 2, 590, "¿Cuánto pesa en la Tierra?", 50, INK, "bold")
        # mochila
        cv.rect(440, 690, 640, 900, fill=BLUE, width=8, radius=40)
        cv.rect(470, 790, 610, 880, fill=YELLOW, width=7, radius=16)
        cv.rect(500, 660, 580, 700, fill=None, width=8, radius=18)
    countdown(cv, W / 2, 1090, t, 2.0, 3)
    sa = pop(t, 5.5)
    card(cv, 60, 960, 1010, 1290, fill=YELLOW, scale=sa)
    if sa > 0.85:
        formula(cv, W / 2, 1060, [("P", C_P), (" = ", INK), ("5", C_M), (" · ", INK), ("9,8", INK)], 84)
        cv.text(W / 2, 1195, "P = 49 N", 120, INK)


def s_resumen(cv, t, D):
    headline(cv, t, 340, [[("En ", False), ("resumen", True)]], 108)
    rows = [(0.6, BLUE, ["Masa: cantidad de materia.", "En kg. No cambia."]),
            (4.5, ORANGE, ["Peso: fuerza de la gravedad.", "En N. Sí cambia."])]
    for k, (t0, col, txt) in enumerate(rows):
        s = pop(t, t0)
        y0 = 500 + k * 255
        card(cv, 60, y0, 1010, y0 + 215, scale=s)
        if s > 0.85:
            check(cv, 150, y0 + 108, 46, col)
            for i, ln in enumerate(txt):
                cv.text(235, y0 + 76 + i * 64, ln, min(46, 46 * 740 / text_w(ln, 46)), INK, "black", "lm")
    s = pop(t, 8.5)
    card(cv, 60, 1010, 1010, 1290, fill=YELLOW, scale=s)
    if s > 0.85:
        big_formula(cv, 1150, 190)


def s_fin(cv, t, D):
    s = pop(t, 0.2)
    if s > 0.02:
        sz = 120 * min(s, 1.05)
        ww = text_w("@quantafyq", sz)
        highlight(cv, W / 2 - ww / 2, 860 - sz * 0.5, W / 2 + ww / 2, 860 + sz * 0.46, grow=ramp(t, 0.5, 0.9))
        cv.text(W / 2, 860, "@quantafyq", sz, INK)
    if pop(t, 0.9) > 0.02:
        cv.text(W / 2, 1010, "Física y Química", 60, INK, "bold")


# --------------------------------------------------------------------------
# Guion: (duración, escena, [(segundo, subtítulo, texto hablado opcional)])
# --------------------------------------------------------------------------
SCENES = [
    (9.0, s_hook, [
        (0.3, "¿Cuánto pesas? Seguro que respondes algo como «50 kilos».",
         "¿Cuánto pesas? Seguro que respondes algo como: cincuenta kilos."),
        (4.5, "Pues eso no es tu peso: es tu masa.")]),
    (11.5, s_masa, [
        (0.3, "La masa es la cantidad de materia que tiene un cuerpo."),
        (4.0, "Se mide en kilogramos, con una balanza."),
        (7.5, "Y no cambia: es la misma aquí, en la Luna o en cualquier lugar.")]),
    (12.5, s_peso, [
        (0.3, "El peso es la fuerza con la que la Tierra te atrae hacia su centro."),
        (4.5, "Como es una fuerza, se mide en newtons, con un dinamómetro.",
         "Como es una fuerza, se mide en niutons, con un dinamómetro."),
        (8.5, "Y sí cambia: depende del lugar en el que estés.")]),
    (13.0, s_formula, [
        (0.3, "El peso se calcula con esta fórmula: P = m · g.",
         "El peso se calcula con esta fórmula: pe es igual a eme por ge."),
        (4.0, "P es el peso, en newtons.", "Pe es el peso, en niutons."),
        (6.0, "m es la masa, en kilogramos.", "Eme es la masa, en kilogramos."),
        (8.5, "Y g es la gravedad: en la Tierra vale 9,8 newtons por kilogramo.",
         "Y ge es la gravedad: en la Tierra vale nueve coma ocho niutons por kilogramo.")]),
    (12.0, s_tierra, [
        (0.3, "Un ejemplo: una persona de 50 kilogramos, en la Tierra.",
         "Un ejemplo: una persona de cincuenta kilogramos, en la Tierra."),
        (3.6, "Multiplicamos la masa por la gravedad: 50 por 9,8.",
         "Multiplicamos la masa por la gravedad: cincuenta por nueve coma ocho."),
        (8.0, "Su peso es de 490 newtons.", "Su peso es de cuatrocientos noventa niutons.")]),
    (14.0, s_luna, [
        (0.3, "¿Y en la Luna? Allí la gravedad es mucho menor: 1,6 newtons por kilogramo.",
         "¿Y en la Luna? Allí la gravedad es mucho menor: uno coma seis niutons por kilogramo."),
        (5.5, "La masa sigue siendo 50 kilogramos, pero el peso baja a 80 newtons.",
         "La masa sigue siendo cincuenta kilogramos, pero el peso baja a ochenta niutons."),
        (10.0, "Por eso los astronautas dan esos saltos tan grandes.")]),
    (10.5, s_compara, [
        (0.3, "Masa y peso no son lo mismo."),
        (2.0, "La masa es materia, se mide en kilogramos con una balanza y no cambia."),
        (6.0, "El peso es una fuerza, se mide en newtons con un dinamómetro y sí cambia.",
         "El peso es una fuerza, se mide en niutons con un dinamómetro y sí cambia.")]),
    (9.5, s_turno, [
        (0.3, "Tu turno. Una mochila tiene 5 kilogramos de masa. ¿Cuánto pesa en la Tierra?",
         "Tu turno. Una mochila tiene cinco kilogramos de masa. ¿Cuánto pesa en la Tierra?"),
        (5.5, "5 por 9,8: pesa 49 newtons.", "Cinco por nueve coma ocho: pesa cuarenta y nueve niutons.")]),
    (12.0, s_resumen, [
        (0.3, "En resumen: la masa es la cantidad de materia, se mide en kilogramos y no cambia."),
        (4.5, "El peso es la fuerza de la gravedad, se mide en newtons y sí cambia.",
         "El peso es la fuerza de la gravedad, se mide en niutons y sí cambia."),
        (8.5, "Y se calcula multiplicando la masa por la gravedad.")]),
    (3.5, s_fin, []),
]

VIDEO = Reel(SCENES, HERE, "masa_peso.mp4")
CAPS, TOTAL = VIDEO.caps, VIDEO.total

if __name__ == "__main__":
    VIDEO.main()
