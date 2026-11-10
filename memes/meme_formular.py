#!/usr/bin/env python3
"""Meme original (1080x1350): «Ven, tengo unos compuestos para formular».

Ilustración propia con el estilo de ../comun/reel.py y la marca @quantafyq.
Uso: python3 meme_formular.py
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "comun"))
import reel  # noqa: E402
from reel import SS, INK, PAPER, ORANGE, BLUE, YELLOW, GREY, LIGHT, text_w, highlight, card  # noqa: E402

W, H = 1080, 1350
RED = (226, 58, 44)
SKIN = (242, 196, 160)
HAIR = (70, 44, 36)


class Lienzo(reel.Canvas):
    def __init__(self, bg):
        self.img = Image.new("RGB", (W * SS, H * SS), bg)
        self.d = ImageDraw.Draw(self.img)

    def arc(self, x0, y0, x1, y1, a0, a1, fill=INK, width=8):
        self.d.arc([x0 * SS, y0 * SS, x1 * SS, y1 * SS], a0, a1, fill=fill, width=int(width * SS))

    def ellipse(self, x, y, rx, ry, fill, width=7):
        self.d.ellipse([(x - rx) * SS, (y - ry) * SS, (x + rx) * SS, (y + ry) * SS], fill=fill,
                       outline=INK if width else None, width=int(width * SS))


def gota(cv, x, y, s):
    pts = [(x, y - 2.3 * s)] + [(x + s * math.cos(a), y + s * math.sin(a))
                               for a in [math.radians(d) for d in range(-25, 206, 11)]]
    cv.poly(pts, BLUE, INK, 5)


def lluvia(cv, y0, y1, seed, evita):
    rnd = random.Random(seed)
    n = 0
    puestas = []
    while n < 16:
        x, y = rnd.uniform(40, W - 40), rnd.uniform(y0 + 40, y1 - 20)
        if any(ax0 < x < ax1 and ay0 < y < ay1 for ax0, ay0, ax1, ay1 in evita):
            continue
        if any(math.hypot(x - px, y - py) < 75 for px, py in puestas):
            continue
        puestas.append((x, y))
        gota(cv, x, y, rnd.uniform(11, 17))
        n += 1


def texto(cv, y0, linea1, linea2):
    """Tarjeta con dos líneas; la segunda va sobre un bloque naranja."""
    s1 = min(62, 62 * 900 / text_w(linea1, 62))
    s2 = min(62, 62 * 880 / text_w(linea2, 62))
    card(cv, 50, y0, W - 50, y0 + 190, shadow=10)
    cv.text(W / 2, y0 + 55, linea1, s1, INK)
    w2 = text_w(linea2, s2)
    highlight(cv, W / 2 - w2 / 2, y0 + 132 - s2 * 0.5, W / 2 + w2 / 2, y0 + 132 + s2 * 0.46)
    cv.text(W / 2, y0 + 132, linea2, s2, INK)


def payaso(cv, x, y):
    for dx, dy, r in ((-112, 0, 58), (112, 0, 58), (-88, -52, 44), (88, -52, 44)):
        cv.circle(x + dx, y + dy, r, fill=RED, width=7)
    cv.circle(x, y, 92, fill=PAPER, width=7)
    for sx in (-1, 1):
        cv.poly([(x + sx * 40, y - 62), (x + sx * 54, y - 22), (x + sx * 40, y + 10), (x + sx * 26, y - 22)], BLUE, INK, 5)
        cv.ellipse(x + sx * 40, y - 22, 13, 17, INK, 0)
        cv.circle(x + sx * 44, y - 28, 5, fill=PAPER, width=0)
        cv.circle(x + sx * 62, y + 26, 15, fill=(244, 150, 140), width=0)
    cv.arc(x - 58, y - 30, x + 58, y + 62, 20, 160, RED, 13)
    cv.circle(x, y + 2, 21, fill=RED, width=6)


def matraz(cv, x, y):
    cv.poly([(x - 16, y - 70), (x + 16, y - 70), (x + 16, y - 25), (x + 55, y + 55), (x - 55, y + 55), (x - 16, y - 25)],
            PAPER, INK, 7)
    cv.poly([(x - 30, y + 5), (x + 30, y + 5), (x + 50, y + 50), (x - 50, y + 50)], ORANGE)
    cv.rect(x - 24, y - 82, x + 24, y - 66, fill=PAPER, width=6, radius=6)
    cv.circle(x - 8, y + 30, 6, fill=PAPER, width=0)
    cv.circle(x + 14, y + 18, 4, fill=PAPER, width=0)


def alumna(cv, x, y):
    cv.poly([(x - 330, 1350), (x - 250, y + 190), (x - 120, y + 125), (x + 120, y + 125), (x + 250, y + 190),
             (x + 330, 1350)], YELLOW, INK, 8)
    cv.circle(x, y - 10, 192, fill=YELLOW, width=8)
    cv.circle(x, y + 12, 136, fill=SKIN, width=7)
    for k in range(9):                              # flequillo rizado
        a = math.radians(200 + k * 17.5)
        cv.circle(x + 122 * math.cos(a), y + 12 + 122 * math.sin(a), 34, fill=HAIR, width=6)
    for sx in (-1, 1):                              # gafas, ojos entornados y cejas
        cv.rect(x + sx * 58 - 46, y - 18, x + sx * 58 + 46, y + 52, fill=PAPER, width=8, radius=20)
        cv.circle(x + sx * 58, y + 26, 13, fill=INK, width=0)
        cv.line([(x + sx * 58 - 40, y + 8), (x + sx * 58 + 40, y + 8)], INK, 8)
    cv.line([(x - 12, y + 14), (x + 12, y + 14)], INK, 8)
    cv.line([(x - 100, y - 44), (x - 22, y - 34)], INK, 10)
    cv.line([(x + 22, y - 52), (x + 100, y - 66)], INK, 10)
    cv.line([(x - 26, y + 96), (x + 30, y + 88)], INK, 9)   # boca: no está convencida


def main():
    cv = Lienzo((60, 64, 88))
    # --- viñeta 1: el payaso en la alcantarilla
    cv.rect(-10, -10, W + 10, 170, fill=(128, 126, 140), width=7)
    cv.rect(-10, 170, W + 10, 440, fill=(96, 94, 110), width=7)
    cv.rect(150, 205, 930, 410, fill=(14, 14, 18), width=7, radius=34)
    payaso(cv, 480, 318)
    matraz(cv, 760, 318)
    lluvia(cv, 0, 430, 4, [(130, 150, 950, 460)])
    texto(cv, 425, "Ven, tengo unos", "compuestos para formular")
    # --- banda central con la marca
    cv.rect(-10, 640, W + 10, 712, fill=INK, width=0)
    cv.text(W / 2, 676, "@quantafyq", 46, PAPER)
    # --- viñeta 2: la alumna con chubasquero
    cv.rect(-10, 712, W + 10, H + 10, fill=(150, 172, 204), width=0)
    lluvia(cv, 712, 1140, 9, [(300, 712, 780, 1350)])
    alumna(cv, 540, 930)
    texto(cv, 1135, "¿Pero son", "oxoácidos u oxisales?")
    out = os.path.join(HERE, "meme_formular.png")
    cv.final().save(out)
    print(out)


if __name__ == "__main__":
    main()
