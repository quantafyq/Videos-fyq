#!/usr/bin/env python3
"""
Vídeo vertical (1080x1920): «Óxidos» — qué son, cómo se formulan y cómo se nombran.

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
    Reel, W, INK, PAPER, ORANGE, BLUE, GREY, LIGHT, YELLOW, GREEN, CREAM,
    pop, ramp, ease, mix, text_w, formula, formula_runs, formula_w, fit,
    headline, sticker, card, chip, atom, check, strike, countdown,
)

DARK = (58, 56, 68)
RUST = (196, 92, 38)


# --------------------------------------------------------------------------
# Ilustraciones
# --------------------------------------------------------------------------
def badge(cv, x, y, s, r=185):
    if s <= 0.02:
        return False
    cv.circle(x + 10, y + 12, r * s, fill=INK, width=0)
    cv.circle(x, y, r * s, fill=PAPER)
    return s > 0.85


def rot(pts, ang, x, y):
    c, s = math.cos(ang), math.sin(ang)
    return [(x + px * c - py * s, y + px * s + py * c) for px, py in pts]


def nail(cv, x, y):
    a = math.radians(-32)
    cv.poly(rot([(-95, -15), (85, -15), (128, 0), (85, 15), (-95, 15)], a, x, y), LIGHT, INK, 7)
    cv.poly(rot([(-122, -46), (-95, -46), (-95, 46), (-122, 46)], a, x, y), LIGHT, INK, 7)
    for px, py, r in ((-50, -2, 15), (-8, 5, 12), (30, -4, 16), (64, 3, 10)):
        (bx, by), = rot([(px, py)], a, x, y)
        cv.circle(bx, by, r, fill=RUST, width=5)


def can(cv, x, y, t):
    cv.rect(x - 64, y - 62, x + 64, y + 112, fill=BLUE, width=7, radius=18)
    cv.rect(x - 64, y - 62, x + 64, y - 30, fill=LIGHT, width=7, radius=12)
    cv.circle(x, y + 40, 30, fill=PAPER, width=6)
    for k, (dx, dy, r) in enumerate(((-34, -98, 13), (16, -124, 17), (50, -92, 10))):
        cv.circle(x + dx, y + dy - 7 * math.sin(t * 3 + k * 2), r, fill=PAPER, width=5)


def sand(cv, x, y):
    cv.circle(x + 78, y - 78, 34, fill=ORANGE, width=7)
    pts = [(x + 140 * math.cos(a), y + 80 - 120 * math.sin(a)) for a in [i * math.pi / 24 for i in range(25)]]
    cv.poly(pts, YELLOW, INK, 7)
    for dx, dy in ((-60, 40), (-10, 10), (40, 45), (-30, 60), (70, 62), (10, 55)):
        cv.circle(x + dx, y + dy, 5, fill=INK, width=0)


def lines(cv, x, y, texts, size, style="bold", color=INK, lh=1.25, anchor="lm"):
    for k, s in enumerate(texts):
        cv.text(x, y + k * size * lh, s, size, color, style, anchor)


# --------------------------------------------------------------------------
# Escenas
# --------------------------------------------------------------------------
def s_hook(cv, t, D):
    if t < 5.0:
        headline(cv, t, 330, [[("¿Qué tienen", False)], [("en común?", True)]], 108)
    else:
        headline(cv, t, 330, [[("Los tres son", False)], [("óxidos", True)]], 108, t0=5.0)
    items = [(290, 760, 0.6, nail), (790, 760, 1.8, can), (540, 1090, 3.0, sand)]
    for x, y, t0, icon in items:
        if badge(cv, x, y, pop(t, t0)):
            if icon is can:
                icon(cv, x, y - 20, t)
            else:
                icon(cv, x, y)
    sticker(cv, 400, 915, "Fe2O3", 62, -8, YELLOW, pop(t, 5.3))
    sticker(cv, 880, 915, "CO2", 62, 8, YELLOW, pop(t, 5.6))
    sticker(cv, 680, 1245, "SiO2", 62, -6, YELLOW, pop(t, 5.9))


def s_que_es(cv, t, D):
    headline(cv, t, 310, [[("Un óxido es", False)], [("oxígeno", True)], [("+ otro elemento", False)]], 96)
    atom(cv, 390, 930, 165, "O", BLUE, PAPER, pop(t, 0.8))
    u = ease((t - 1.8) / 0.7)
    if t > 1.8:
        atom(cv, 1250 - (1250 - 705) * u, 960, 135, "?", GREY, PAPER)
    sticker(cv, 520, 760, "−2", 96, 10, YELLOW, pop(t, 5.0))
    s = pop(t, 5.6)
    if s > 0.02:
        cv.text(W / 2, 1220 + (1 - min(1, s)) * 30, "El oxígeno: siempre −2", 58, INK, "black")


def tipo_card(cv, t, t0, y0, atoms, chip_txt, chip_col, name, ej, ang):
    s = pop(t, t0)
    card(cv, 60, y0, 1010, y0 + 330, scale=s)
    if s < 0.85:
        return
    for dx, dy, r, lab, col in atoms:
        atom(cv, 60 + dx, y0 + dy, r, lab, col, PAPER)
    chip(cv, 440, y0 + 85, chip_txt, 30, chip_col)
    cv.text(440, y0 + 185, name, fit(name, 56, 530), INK, "black", "lm")
    sticker(cv, 830, y0 + 275, ej, 60, ang, YELLOW, pop(t, t0 + 0.6))


def s_tipos(cv, t, D):
    headline(cv, t, 340, [[("Hay ", False), ("dos tipos", True)]], 108)
    tipo_card(cv, t, 2.5, 520, [(140, 170, 82, "Fe", GREY), (258, 198, 62, "O", BLUE)],
              "METAL + OXÍGENO", BLUE, "óxido metálico", "Fe2O3", -6)
    tipo_card(cv, t, 7.5, 910, [(95, 190, 54, "O", BLUE), (182, 172, 62, "C", DARK), (270, 190, 54, "O", BLUE)],
              "NO METAL + OXÍGENO", ORANGE, "óxido no metálico", "CO2", 6)


def cross_stage(cv, t, sym, q, y, tA, tQ, tX, tR, size=220):
    """Símbolos arriba, sus números de oxidación debajo y, cruzando, la fórmula."""
    xs, xo = 330, 750
    sa = pop(t, tA)
    if sa > 0.02:
        cv.text(xs, y, sym, size * min(sa, 1.05), INK)
    so = pop(t, tA + 0.5)
    if so > 0.02:
        cv.text(xo, y, "O", size * min(so, 1.05), BLUE)
    yq = y + 175
    sticker(cv, xs, yq, f"{q}+" if q > 1 else "+", 74, -6, YELLOW, pop(t, tQ))
    sticker(cv, xo, yq, "2−", 74, 6, YELLOW, pop(t, tQ + 0.5))
    # fórmula cruzada
    yr = y + 440
    parts = [(sym, INK), ("2", ORANGE), ("O", BLUE)] + ([(str(q), ORANGE)] if q > 1 else [])
    rs = size * 0.9
    runs, w = formula_runs(parts, rs)
    x0 = W / 2 - w / 2
    subs = [x0 + dx + text_w(s, fs) / 2 for s, dx, dy, fs, col in runs if col == ORANGE]
    sub_m = subs[0]
    sub_o = subs[1] if len(subs) > 1 else x0 + w + 20
    u = ramp(t, tX, tX + 0.9)
    if u > 0:
        y0, y1 = yq + 62, yr - rs * 0.25
        cv.arrow(xs, y0, xs + (sub_o - xs) * u, y0 + (y1 - y0) * u, ORANGE, 11, 36)
        cv.arrow(xo, y0, xo + (sub_m - xo) * u, y0 + (y1 - y0) * u, ORANGE, 11, 36)
    sr = pop(t, tR)
    if sr > 0.02:
        formula(cv, W / 2, yr + (1 - min(1, sr)) * 30, parts, rs)
    return x0, w, yr


def s_formular(cv, t, D):
    headline(cv, t, 340, [[("Así se ", False), ("formula", True)]], 108)
    chip(cv, W / 2, 500, "1.º el otro elemento · 2.º el oxígeno", 34, INK, PAPER, pop(t, 1.6), anchor="c")
    cross_stage(cv, t, "Fe", 3, 690, 0.8, 4.5, 8.5, 9.8)
    sticker(cv, 790, 1292, "¡hecho!", 54, -6, PAPER, pop(t, 12.5))


def s_simplifica(cv, t, D):
    headline(cv, t, 320, [[("Y si se puede,", False)], [("simplifica", True)]], 100)
    x0, w, yr = cross_stage(cv, t, "Ca", 2, 670, 0.8, 3.0, 4.2, 5.4, size=190)
    strike(cv, x0 - 10, x0 + w + 10, yr + 10, ramp(t, 8.0, 8.5))
    sticker(cv, 620, yr + 172, "CaO", 92, -5, YELLOW, pop(t, 8.6))


def s_nombrar(cv, t, D):
    headline(cv, t, 340, [[("Así se ", False), ("nombra", True)]], 108)
    s = pop(t, 0.6)
    if s > 0.02:
        formula(cv, W / 2, 610, [("Fe", INK), ("2", ORANGE), ("O", INK), ("3", ORANGE)], 190 * min(s, 1.05))
    sa = pop(t, 3.0)
    card(cv, 60, 770, 1010, 990, scale=sa)
    if sa > 0.85:
        chip(cv, 100, 832, "CON PREFIJOS", 30, BLUE)
        n = [("tri", ORANGE), ("óxido de ", INK), ("di", ORANGE), ("hierro", INK)]
        formula(cv, 100, 925, n, fit(n, 74, 870), align="left")
    sb = pop(t, 8.5)
    card(cv, 60, 1040, 1010, 1260, scale=sb)
    if sb > 0.85:
        chip(cv, 100, 1102, "CON N.º DE OXIDACIÓN", 30, ORANGE)
        n = [("óxido de hierro", INK), ("(III)", ORANGE)]
        formula(cv, 100, 1195, n, fit(n, 74, 870), align="left")


def ej_card(cv, t, t0, y0, f, n1, n2, note=None):
    s = pop(t, t0)
    card(cv, 60, y0, 1010, y0 + 215, scale=s)
    if s < 0.85:
        return
    formula(cv, 215, y0 + 105, f, fit(f, 104, 250))
    cv.line([(370, y0 + 35), (370, y0 + 180)], LIGHT, 5)
    formula(cv, 405, y0 + 75, n1, fit(n1, 48, 570), align="left")
    if note:
        cv.text(405, y0 + 150, n2, 32, GREY, "bold", "lm")
    else:
        formula(cv, 405, y0 + 150, n2, fit(n2, 44, 570, "bold"), style="bold", align="left")


def s_ejemplos(cv, t, D):
    headline(cv, t, 340, [[("Más ", False), ("ejemplos", True)]], 108)
    ej_card(cv, t, 1.5, 480, "CO", [("mon", ORANGE), ("óxido de carbono", INK)],
            [("óxido de carbono", INK), ("(II)", ORANGE)])
    ej_card(cv, t, 6.0, 735, "CO2", [("di", ORANGE), ("óxido de carbono", INK)],
            [("óxido de carbono", INK), ("(IV)", ORANGE)])
    ej_card(cv, t, 10.5, 990, "CaO", [("óxido de calcio", INK)], "solo tiene +2: sin número romano", note=True)


def s_ojo(cv, t, D):
    sticker(cv, W / 2, 320, "¡OJO!", 120, -7, YELLOW, pop(t, 0.2))
    headline(cv, t, 500, [[("con los ", False), ("halógenos", True)]], 84, t0=0.5)
    for k, (lab, x) in enumerate((("F", 225), ("Cl", 435), ("Br", 645), ("I", 855))):
        atom(cv, x, 680, 74, lab, GREEN, PAPER, pop(t, 1.0 + 0.3 * k))
    s = pop(t, 4.0)
    if s > 0.02:
        formula(cv, 350, 920, [("O", BLUE), ("Cl2", INK)], 200 * min(s, 1.05))
    sticker(cv, 835, 900, "el O, delante", 38, 6, PAPER, pop(t, 4.8))
    sb = pop(t, 8.0)
    card(cv, 60, 1070, 1010, 1290, scale=sb)
    if sb > 0.85:
        n = [("di", ORANGE), ("cloruro de oxígeno", INK)]
        formula(cv, W / 2, 1140, n, fit(n, 70, 880))
        cv.text(W / 2, 1232, "óxido de cloro", 46, GREY, "bold")
        ww = text_w("óxido de cloro", 46, "bold")
        strike(cv, W / 2 - ww / 2 - 12, W / 2 + ww / 2 + 12, 1232, ramp(t, 8.8, 9.2), width=9)


def practica(cv, t, verbo, prompt, answer, extra, psize):
    sticker(cv, W / 2, 320, "TU TURNO", 84, -5, ORANGE, pop(t, 0.1), ink=INK, style="black")
    s = pop(t, 0.5)
    if s > 0.02:
        cv.text(W / 2, 500, verbo, 66, INK, "bold")
        formula(cv, W / 2, 700, prompt, fit(prompt, psize, 940) * min(s, 1.05))
    countdown(cv, W / 2, 1040, t, 1.8, 3)
    sa = pop(t, 5.5)
    card(cv, 60, 900, 1010, 1220, fill=YELLOW, scale=sa)
    if sa > 0.85:
        formula(cv, W / 2, 1015, answer, fit(answer, 150, 880))
        cv.text(W / 2, 1150, extra, min(40, 40 * 880 / text_w(extra, 40, "bold")), INK, "bold")


def s_p1(cv, t, D):
    practica(cv, t, "Nombra", [("Al", INK), ("2", ORANGE), ("O", INK), ("3", ORANGE)],
             [("óxido de aluminio", INK)], "o también: trióxido de dialuminio", 210)


def s_p2(cv, t, D):
    practica(cv, t, "Formula", [("óxido de cobre", INK), ("(I)", ORANGE)],
             [("Cu", INK), ("2", ORANGE), ("O", INK)], "cobre +1 · oxígeno −2 · se cruzan", 110)


def s_resumen(cv, t, D):
    headline(cv, t, 340, [[("En ", False), ("resumen", True)]], 108)
    rows = [(0.6, ["Óxido =", "oxígeno + otro elemento"]),
            (4.0, ["El O actúa con −2:", "cruza y simplifica"]),
            (8.0, ["Nombre: con prefijos", "o con número romano"])]
    for k, (t0, txt) in enumerate(rows):
        s = pop(t, t0)
        y0 = 500 + k * 265
        card(cv, 60, y0, 1010, y0 + 220, scale=s)
        if s > 0.85:
            check(cv, 160, y0 + 110, 50)
            sz = min(48, min(48 * 720 / text_w(x, 48) for x in txt))
            lines(cv, 250, y0 + 80, txt, sz, "black")


def s_fin(cv, t, D):
    s = pop(t, 0.2)
    if s > 0.02:
        sz = 120 * min(s, 1.05)
        from reel import highlight
        ww = text_w("@quantafyq", sz)
        highlight(cv, W / 2 - ww / 2, 860 - sz * 0.5, W / 2 + ww / 2, 860 + sz * 0.46, grow=ramp(t, 0.5, 0.9))
        cv.text(W / 2, 860, "@quantafyq", sz, INK)
    s2 = pop(t, 0.9)
    if s2 > 0.02:
        cv.text(W / 2, 1010, "Física y Química", 60, INK, "bold")


# --------------------------------------------------------------------------
# Guion: (duración, escena, [(segundo, subtítulo, texto hablado opcional)])
# --------------------------------------------------------------------------
SCENES = [
    (8.0, s_hook, [
        (0.3, "Un clavo oxidado, las burbujas de tu refresco y la arena de la playa."),
        (5.0, "Los tres son óxidos.")]),
    (10.0, s_que_es, [
        (0.3, "Un óxido es la combinación del oxígeno con otro elemento."),
        (5.0, "Y el oxígeno actúa siempre con número de oxidación −2.",
         "Y el oxígeno actúa siempre con número de oxidación menos dos.")]),
    (12.5, s_tipos, [
        (0.3, "Hay dos tipos de óxidos."),
        (2.5, "Con un metal forma un óxido metálico, como el óxido de hierro: la herrumbre."),
        (7.5, "Con un no metal forma un óxido no metálico, como el dióxido de carbono.")]),
    (15.0, s_formular, [
        (0.3, "Para formularlo, escribe primero el otro elemento y después el oxígeno."),
        (4.5, "Cada uno con su número de oxidación: hierro, +3; oxígeno, −2.",
         "Cada uno con su número de oxidación: hierro, más tres; oxígeno, menos dos."),
        (8.5, "Ahora crúzalos: el 3 baja al oxígeno y el 2 baja al hierro.",
         "Ahora crúzalos: el tres baja al oxígeno, y el dos baja al hierro."),
        (12.5, "Resultado: Fe₂O₃.", "Resultado: efe e dos, o tres.")]),
    (12.0, s_simplifica, [
        (0.3, "Si los subíndices se pueden simplificar, hazlo."),
        (3.0, "Calcio, +2; oxígeno, −2. Al cruzar queda Ca₂O₂…",
         "Calcio, más dos; oxígeno, menos dos. Al cruzar queda calcio dos, oxígeno dos."),
        (8.0, "Dividimos entre dos y queda CaO.", "Dividimos entre dos y queda ce a, o.")]),
    (14.0, s_nombrar, [
        (0.3, "Para nombrarlo tienes dos formas."),
        (3.0, "Con prefijos, que cuentan los átomos: trióxido de dihierro."),
        (8.5, "O con el número de oxidación en números romanos: óxido de hierro(III).",
         "O con el número de oxidación en números romanos: óxido de hierro tres.")]),
    (15.5, s_ejemplos, [
        (0.3, "Más ejemplos."),
        (1.5, "CO: monóxido de carbono, u óxido de carbono(II).",
         "Ce o: monóxido de carbono, u óxido de carbono dos."),
        (6.0, "CO₂: dióxido de carbono, u óxido de carbono(IV).",
         "Ce o dos: dióxido de carbono, u óxido de carbono cuatro."),
        (10.5, "CaO: óxido de calcio. El calcio solo tiene un número de oxidación, así que no se indica.",
         "Ce a o: óxido de calcio. El calcio solo tiene un número de oxidación, así que no se indica.")]),
    (12.5, s_ojo, [
        (0.3, "Ojo con los halógenos: flúor, cloro, bromo y yodo."),
        (4.0, "Con ellos, el oxígeno se escribe delante y el nombre cambia."),
        (8.0, "OCl₂ es dicloruro de oxígeno, no óxido de cloro.",
         "O ce ele dos es dicloruro de oxígeno, no óxido de cloro.")]),
    (9.5, s_p1, [
        (0.3, "Tu turno. Nombra Al₂O₃.", "Tu turno. Nombra a ele dos, o tres."),
        (5.5, "Óxido de aluminio, o trióxido de dialuminio.")]),
    (9.5, s_p2, [
        (0.3, "Ahora formula el óxido de cobre(I).", "Ahora formula el óxido de cobre uno."),
        (5.5, "Cobre, +1; oxígeno, −2. Al cruzar: Cu₂O.",
         "Cobre, más uno; oxígeno, menos dos. Al cruzar: ce u dos, o.")]),
    (12.0, s_resumen, [
        (0.3, "En resumen: un óxido es oxígeno más otro elemento."),
        (4.0, "El oxígeno actúa con −2: cruza los números y simplifica.",
         "El oxígeno actúa con menos dos: cruza los números y simplifica."),
        (8.0, "Y se nombra con prefijos o con el número de oxidación en romanos.")]),
    (3.5, s_fin, []),
]

VIDEO = Reel(SCENES, HERE, "oxidos.mp4")
CAPS, TOTAL = VIDEO.caps, VIDEO.total

if __name__ == "__main__":
    VIDEO.main()
