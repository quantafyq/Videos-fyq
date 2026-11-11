"""
Estilo «reel» para vídeos verticales (1080x1920):
fondo crema con trama de puntos, titulares muy gruesos con una parte
resaltada sobre un bloque naranja, ilustraciones planas con contorno negro
y pegatinas inclinadas.

Tipografía: Archivo (variable, licencia OFL, en comun/fuentes/).

Cada vídeo define una lista de escenas (duración, función, narración) y usa
la clase `Reel` para renderizar. Si existe `narracion.json` (creado con
`narrar.py --medir`), cada tramo se alarga para que quepa la voz.
"""

import argparse
import bisect
import json
import math
import multiprocessing as mp
import os
import subprocess
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
SS = 2
FPS = 30
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_FILE = os.path.join(HERE, "fuentes", "Archivo.ttf")

CREAM = (246, 234, 200)
PAPER = (255, 250, 236)
INK = (22, 22, 26)
ORANGE = (242, 92, 40)
BLUE = (47, 78, 228)
GREY = (92, 90, 104)
LIGHT = (176, 172, 180)
YELLOW = (247, 201, 62)
GREEN = (34, 160, 104)
MARCA = "@quantafyq"

STYLES = {"black": (900, 125), "bold": (800, 108), "text": (640, 100)}


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ramp(t, t0, t1):
    if t1 <= t0:
        return 1.0 if t >= t0 else 0.0
    return ease((t - t0) / (t1 - t0))


def pop(t, t0, dur=0.45):
    """Escala 0 -> 1 con un pequeño rebote."""
    u = clamp((t - t0) / dur)
    if u <= 0:
        return 0.0
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (u - 1) ** 3 + c1 * (u - 1) ** 2


def mix(c1, c2, a):
    a = clamp(a)
    return tuple(int(round(c1[i] + (c2[i] - c1[i]) * a)) for i in range(3))


_fonts = {}


def font(size, style="black"):
    key = (max(4, int(round(size * SS))), style)
    if key not in _fonts:
        f = ImageFont.truetype(FONT_FILE, key[0])
        f.set_variation_by_axes(list(STYLES[style]))
        _fonts[key] = f
    return _fonts[key]


def text_w(s, size, style="black"):
    return font(size, style).getlength(s) / SS


_bg = None


def background():
    global _bg
    if _bg is None:
        img = Image.new("RGB", (W * SS, H * SS), CREAM)
        d = ImageDraw.Draw(img)
        dot = mix(CREAM, (214, 196, 150), 0.55)
        step = 18 * SS
        for j, y in enumerate(range(step // 2, H * SS, step)):
            for x in range(step // 2 + (step // 2 if j % 2 else 0), W * SS, step):
                d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=dot)
        _bg = img
    return _bg


class Canvas:
    def __init__(self):
        self.img = background().copy()
        self.d = ImageDraw.Draw(self.img)

    def circle(self, x, y, r, fill=None, outline=INK, width=8):
        if r <= 0:
            return
        self.d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=fill,
                       outline=outline if width else None, width=int(width * SS))

    def rect(self, x0, y0, x1, y1, fill=None, outline=INK, width=8, radius=0):
        if x1 <= x0 or y1 <= y0:
            return
        self.d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=radius * SS, fill=fill,
                                 outline=outline if width else None, width=int(width * SS))

    def poly(self, pts, fill, outline=None, width=0):
        p = [(x * SS, y * SS) for x, y in pts]
        self.d.polygon(p, fill=fill)
        if outline and width:
            self.d.line(p + [p[0], p[1]], fill=outline, width=int(width * SS), joint="curve")

    def line(self, pts, fill=INK, width=8):
        self.d.line([(x * SS, y * SS) for x, y in pts], fill=fill, width=max(1, int(width * SS)), joint="curve")
        r = width / 2
        for x, y in (pts[0], pts[-1]):
            self.d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=fill)

    def arrow(self, x0, y0, x1, y1, fill=INK, width=10, head=34):
        ang = math.atan2(y1 - y0, x1 - x0)
        bx, by = x1 - head * 0.8 * math.cos(ang), y1 - head * 0.8 * math.sin(ang)
        self.line([(x0, y0), (bx, by)], fill, width)
        px, py = math.cos(ang + math.pi / 2), math.sin(ang + math.pi / 2)
        hx, hy = x1 - head * math.cos(ang), y1 - head * math.sin(ang)
        self.poly([(x1, y1), (hx + px * head * 0.55, hy + py * head * 0.55),
                   (hx - px * head * 0.55, hy - py * head * 0.55)], fill)

    def text(self, x, y, s, size, fill=INK, style="black", anchor="mm"):
        if size < 2:
            return
        self.d.text((x * SS, y * SS), s, font=font(size, style), fill=fill, anchor=anchor)

    def paste(self, im, x, y, scale=1.0):
        """Pega una imagen RGBA (a escala SS) centrada en (x, y)."""
        if scale <= 0.02:
            return
        if abs(scale - 1) > 0.01:
            im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
        self.img.paste(im, (int(x * SS - im.width / 2), int(y * SS - im.height / 2)), im)

    def final(self):
        return self.img.reduce(SS)


# --------------------------------------------------------------------------
# Fórmulas (los números tras una letra o un paréntesis son subíndices)
# --------------------------------------------------------------------------
def _norm(parts, color=INK):
    if isinstance(parts, str):
        return [(parts, color)]
    return [(p, color) if isinstance(p, str) else p for p in parts]


def formula_runs(parts, size, style="black", color=INK):
    runs, x, prev = [], 0.0, ""
    for text, col in _norm(parts, color):
        i = 0
        while i < len(text):
            sub = text[i].isdigit() and (prev.isalpha() or prev == ")")
            j = i + 1
            if sub:
                while j < len(text) and text[j].isdigit():
                    j += 1
            else:
                while j < len(text) and not (text[j].isdigit() and (text[j - 1].isalpha() or text[j - 1] == ")")):
                    j += 1
            s = text[i:j]
            fs = size * 0.6 if sub else size
            runs.append((s, x, 0.2 * size if sub else 0.0, fs, col))
            x += font(fs, style).getlength(s) / SS
            prev = s[-1]
            i = j
    return runs, x


def formula_w(parts, size, style="black"):
    return formula_runs(parts, size, style)[1]


def fit(parts, size, maxw, style="black"):
    w = formula_w(parts, size, style)
    return size if w <= maxw else size * maxw / w


def formula(cv, x, y, parts, size, style="black", align="center", color=INK, draw=None, off=(0, 0)):
    """Dibuja la fórmula centrada verticalmente en y. Devuelve (x_izq, ancho)."""
    runs, w = formula_runs(parts, size, style, color)
    x0 = x - w / 2 if align == "center" else (x - w if align == "right" else x)
    d = draw or cv.d
    by = y + 0.36 * size
    for s, dx, dy, fs, col in runs:
        d.text(((x0 + dx) * SS + off[0], (by + dy) * SS + off[1]), s, font=font(fs, style), fill=col, anchor="ls")
    return x0, w


# --------------------------------------------------------------------------
# Elementos de estilo
# --------------------------------------------------------------------------
def highlight(cv, x0, y0, x1, y1, color=ORANGE, grow=1.0):
    """Bloque inclinado (como pintado con rotulador) detrás de un texto."""
    if grow <= 0:
        return
    x1 = x0 + (x1 - x0) * grow
    cv.poly([(x0 - 14, y0 + 10), (x1 + 16, y0 - 8), (x1 + 8, y1 + 2), (x0 - 20, y1 + 14)], color)


def headline(cv, t, y, lines, size=104, t0=0.0, maxw=980, gap=1.12):
    """Titular en varias líneas. Cada línea es una lista de (texto, resaltado)."""
    for k, segs in enumerate(lines):
        full = "".join(s for s, _ in segs)
        sz = min(size, size * maxw / max(1, text_w(full, size)))
        a = pop(t, t0 + 0.12 * k)
        if a <= 0:
            continue
        yy = y + k * size * gap + (1 - min(1, a)) * 40
        x = W / 2 - text_w(full, sz) / 2
        for s, hl in segs:
            w = text_w(s, sz)
            if hl:
                st = s.strip()
                lead = text_w(s[:len(s) - len(s.lstrip())], sz) if s != st else 0
                highlight(cv, x + lead, yy - sz * 0.5, x + lead + text_w(st, sz), yy + sz * 0.46,
                          grow=ramp(t, t0 + 0.25 + 0.12 * k, t0 + 0.6 + 0.12 * k))
            cv.text(x, yy, s, sz, INK, "black", "lm")
            x += w


_stickers = {}


def sticker(cv, x, y, parts, size=64, angle=-8, fill=PAPER, scale=1.0, ink=INK, style="black", pad=26):
    """Pegatina inclinada con borde negro."""
    if scale <= 0.02:
        return
    key = (str(parts), size, angle, fill, ink, style, pad)
    if key not in _stickers:
        w = formula_w(parts, size, style) + 2 * pad
        h = size * 1.25 + pad * 0.8
        im = Image.new("RGBA", (int(w * SS) + 8, int(h * SS) + 8), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([4, 4, im.width - 4, im.height - 4], radius=int(14 * SS), fill=fill + (255,),
                            outline=ink + (255,), width=int(7 * SS))
        runs, fw = formula_runs(parts, size, style, ink)
        bx = (im.width - fw * SS) / 2
        by = im.height / 2 + 0.36 * size * SS
        for s, dx, dy, fs, col in runs:
            d.text((bx + dx * SS, by + dy * SS), s, font=font(fs, style), fill=col + (255,), anchor="ls")
        _stickers[key] = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    cv.paste(_stickers[key], x, y, scale)


def card(cv, x0, y0, x1, y1, fill=PAPER, scale=1.0, shadow=12, radius=28):
    """Tarjeta con borde negro y sombra plana."""
    if scale <= 0.02:
        return
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    s = min(scale, 1.06)
    x0, x1 = cx + (x0 - cx) * s, cx + (x1 - cx) * s
    y0, y1 = cy + (y0 - cy) * s, cy + (y1 - cy) * s
    cv.rect(x0 + shadow, y0 + shadow, x1 + shadow, y1 + shadow, fill=INK, width=0, radius=radius)
    cv.rect(x0, y0, x1, y1, fill=fill, radius=radius)


def chip(cv, x, y, s, size=34, fill=BLUE, color=PAPER, scale=1.0, anchor="l"):
    if scale <= 0.02:
        return
    w = text_w(s, size, "bold") + 44
    x0 = x if anchor == "l" else x - w / 2
    cv.rect(x0, y - size * 0.85, x0 + w, y + size * 0.85, fill=fill, width=6, radius=size * 0.85)
    cv.text(x0 + w / 2, y, s, size, color, "bold")


def atom(cv, x, y, r, label, fill=BLUE, color=PAPER, scale=1.0):
    r *= scale
    if r < 2:
        return
    cv.circle(x + 8, y + 10, r, fill=INK, width=0)
    cv.circle(x, y, r, fill=fill)
    cv.circle(x - r * 0.42, y - r * 0.42, r * 0.16, fill=mix(fill, PAPER, 0.55), width=0)
    cv.text(x, y + r * 0.04, label, r * (0.95 if len(label) == 1 else 0.72), color)


def check(cv, x, y, s=44, color=GREEN, scale=1.0):
    s *= scale
    if s < 2:
        return
    cv.circle(x, y, s, fill=color, width=7)
    cv.line([(x - s * 0.45, y + s * 0.02), (x - s * 0.12, y + s * 0.34), (x + s * 0.48, y - s * 0.32)], PAPER, s * 0.2)


def strike(cv, x0, x1, y, grow=1.0, color=ORANGE, width=14):
    if grow <= 0:
        return
    cv.line([(x0, y + 8), (x0 + (x1 - x0) * grow, y - 8)], color, width)


def countdown(cv, x, y, t, t0, secs=3):
    """Cuenta atrás en un círculo; desaparece al terminar."""
    if t < t0 or t >= t0 + secs:
        return
    n = secs - int(t - t0)
    u = (t - t0) % 1.0
    s = 1 + 0.12 * (1 - ease(u * 3))
    cv.circle(x, y, 92 * s, fill=YELLOW)
    cv.text(x, y + 4, str(n), 110 * s, INK)


# --------------------------------------------------------------------------
# Render
# --------------------------------------------------------------------------
class Reel:
    def __init__(self, scenes, here, out_name):
        self.here = here
        self.out_name = out_name
        durs = None
        jp = os.path.join(here, "narracion.json")
        if os.path.exists(jp):
            with open(jp, encoding="utf-8") as fh:
                durs = json.load(fh)["durs"]
        self.scenes, self.starts, self.caps = [], [], []
        acc, k = 0.0, 0
        for d, f, caps in scenes:
            old = [0.0] + [c[0] for c in caps] + [d]
            new = [0.0, old[1] if caps else d]
            for i in range(len(caps)):
                seg = old[i + 2] - old[i + 1]
                if durs is not None and k + i < len(durs):
                    seg = max(seg, durs[k + i] + 0.5)
                new.append(new[-1] + seg)
            dn = new[-1]
            self.starts.append(acc)
            self.scenes.append((dn, f, d, (new, old)))
            for i, c in enumerate(caps):
                t1 = new[i + 2] if i + 1 < len(caps) else dn - 0.15
                self.caps.append((acc + new[i + 1], acc + t1, c[1]) + ((c[2],) if len(c) > 2 else ()))
            k += len(caps)
            acc += dn
        self.total = acc

    @staticmethod
    def warp(t, maps):
        new, old = maps
        i = max(0, min(len(new) - 2, bisect.bisect_right(new, t) - 1))
        n0, n1, o0, o1 = new[i], new[i + 1], old[i], old[i + 1]
        return o0 if n1 <= n0 else o0 + (t - n0) * (o1 - o0) / (n1 - n0)

    def draw_caption(self, cv, T):
        for c in self.caps:
            t0, t1, txt = c[0], c[1], c[2]
            if t0 <= T < t1:
                s = min(1.0, pop(T, t0, 0.25))
                lines = textwrap.wrap(txt, 34)
                size = 44
                lh = size * 1.28
                hh = lh * len(lines) + 44
                ww = max(text_w(ln, size, "bold") for ln in lines) + 70
                cy = 1440
                y0 = cy - hh / 2 + (1 - s) * 30
                cv.rect(W / 2 - ww / 2 + 8, y0 + 8, W / 2 + ww / 2 + 8, y0 + hh + 8, fill=INK, width=0, radius=22)
                cv.rect(W / 2 - ww / 2, y0, W / 2 + ww / 2, y0 + hh, fill=PAPER, width=6, radius=22)
                for k, ln in enumerate(lines):
                    cv.text(W / 2, y0 + 22 + lh * (k + 0.5), ln, size, INK, "bold")
                break

    def render(self, T):
        cv = Canvas()
        for (d, f, d0, maps), s in zip(self.scenes, self.starts):
            if s <= T < s + d:
                f(cv, self.warp(T - s, maps), d0)
                break
        self.draw_caption(cv, T)
        cv.text(W / 2, 150, MARCA, 40, mix(CREAM, INK, 0.75), "bold")
        if getattr(self, "overlay", None):
            self.overlay(cv, T, self.total)
        return cv.final()

    def write_srt(self, path):
        def ts(x):
            ms = int(round(x * 1000))
            h, ms = divmod(ms, 3600000)
            m, ms = divmod(ms, 60000)
            s, ms = divmod(ms, 1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
        with open(path, "w", encoding="utf-8") as fh:
            for k, c in enumerate(self.caps, 1):
                fh.write(f"{k}\n{ts(c[0])} --> {ts(c[1])}\n{c[2]}\n\n")

    def main(self):
        ap = argparse.ArgumentParser()
        ap.add_argument("--preview", type=float, nargs="*")
        ap.add_argument("-o", "--output", default=os.path.join(self.here, self.out_name))
        args = ap.parse_args()
        print(f"Duración total: {self.total:.1f} s")
        if args.preview is not None:
            for s in args.preview:
                p = os.path.join(self.here, f"preview_{s:05.1f}.png")
                self.render(s).save(p)
            return
        srt = os.path.splitext(args.output)[0] + ".srt"
        self.write_srt(srt)
        nfr = int(self.total * FPS)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
               "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
               "-movflags", "+faststart", args.output]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        global _REEL
        _REEL = self
        background()
        with mp.get_context("fork").Pool(os.cpu_count()) as pool:
            for k, buf in enumerate(pool.imap(_frame, range(nfr), chunksize=4)):
                proc.stdin.write(buf)
                if k % 600 == 0:
                    print(f"  fotograma {k}/{nfr}", flush=True)
        proc.stdin.close()
        proc.wait()
        print("vídeo:", args.output, "\nsubtítulos:", srt)


_REEL = None


def _frame(i):
    return _REEL.render(i / FPS).tobytes()
