"""
Herramientas comunes para los vídeos de formulación inorgánica
(oxisales, sales ácidas...).

Reutiliza el lienzo y los colores de ../colisiones/generar_video.py y añade:

* `draw_formula`: dibuja fórmulas con subíndices y cargas (p. ej. "Fe2(SO4)3",
  "SO4^2−"). Las cifras que van detrás de una letra o de un paréntesis se
  escriben como subíndice; lo que va detrás de "^" es la carga (superíndice).
* Escenas genéricas: `free_scene`, `steps_scene`, `cross_scene`,
  `table_scene` y `practice_scene`.
* `run`: renderiza el vídeo, los subtítulos .srt y las vistas previas.

Cada escena de un vídeo es una tupla (duración, función, narración), donde la
narración es una lista de (segundo, texto[, texto_hablado]). El texto hablado
es opcional y sirve para que la voz sintética lea bien las fórmulas.
"""

import argparse
import bisect
import importlib.util
import json
import math
import multiprocessing as mp
import os
import subprocess
import textwrap

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location(
    "base_colisiones", os.path.join(ROOT, "colisiones", "generar_video.py"))
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)

BG, PANEL, GRID = base.BG, base.PANEL, base.GRID
WHITE, GREY, YELLOW = base.WHITE, base.GREY, base.YELLOW
GREEN, RED, ORANGE = base.GREEN, base.RED, base.ORANGE
W, H, FPS, SS = base.W, base.H, base.FPS, base.SS
Canvas, fade, ramp, mix, clamp, ease = base.Canvas, base.fade, base.ramp, base.mix, base.clamp, base.ease
check_mark, cross_mark, font = base.check_mark, base.cross_mark, base.font

# Colores con significado
CAT = (255, 170, 90)     # catión metálico
AN = (100, 178, 255)     # anión
HYD = (120, 225, 150)    # hidrógeno
OXN = YELLOW             # números de oxidación, cargas que se cruzan
MINUS = "−"


# --------------------------------------------------------------------------
# Fórmulas
# --------------------------------------------------------------------------
def _norm(parts):
    if isinstance(parts, str):
        return [(parts, WHITE)]
    out = []
    for p in parts:
        out.append((p, WHITE) if isinstance(p, str) else p)
    return out


def formula_runs(parts, size, bold=True):
    """Divide la fórmula en trozos (texto, x, dy, tamaño, color)."""
    runs = []
    x = 0.0
    prev = ""
    sub_start = None
    for text, col in _norm(parts):
        i = 0
        while i < len(text):
            ch = text[i]
            if ch == "^":
                s = text[i + 1:]
                fs = size * 0.58
                x0 = sub_start if sub_start is not None else x
                runs.append((s, x0, -0.42 * size, fs, col))
                x = max(x, x0 + font(fs, bold).getlength(s) / SS)
                i = len(text)
                prev = s[-1:] if s else prev
                sub_start = None
                break
            if ch.isdigit() and (prev.isalpha() or prev == ")" or (prev.isdigit() and sub_start is not None)):
                j = i
                while j < len(text) and text[j].isdigit():
                    j += 1
                s = text[i:j]
                fs = size * 0.62
                sub_start = x
                runs.append((s, x, 0.26 * size, fs, col))
                x += font(fs, bold).getlength(s) / SS
                prev = s[-1]
                i = j
                continue
            j = i + 1
            while j < len(text) and text[j] != "^" and not (
                    text[j].isdigit() and (text[j - 1].isalpha() or text[j - 1] == ")")):
                j += 1
            s = text[i:j]
            runs.append((s, x, 0.0, size, col))
            x += font(size, bold).getlength(s) / SS
            prev = s[-1]
            sub_start = None
            i = j
    return runs, x


def formula_width(parts, size, bold=True):
    return formula_runs(parts, size, bold)[1]


def fit(parts, size, maxw, bold=True):
    """Tamaño de letra para que la fórmula no pase de `maxw` píxeles."""
    w = formula_width(parts, size, bold)
    return size if w <= maxw else size * maxw / w


def draw_formula(cv, x, y, parts, size, a=1.0, align="center", bold=True, bg=None):
    """Dibuja la fórmula centrada verticalmente en y. Devuelve (x_izq, ancho)."""
    runs, w = formula_runs(parts, size, bold)
    if align == "center":
        x0 = x - w / 2
    elif align == "right":
        x0 = x - w
    else:
        x0 = x
    base_y = y + 0.36 * size
    bgc = bg or cv.bg
    for s, dx, dy, fs, col in runs:
        cv.d.text(((x0 + dx) * SS, (base_y + dy) * SS), s, font=font(fs, bold),
                  fill=mix(bgc, col, a), anchor="ls")
    return x0, w


def wrap_text(cv, x, y, s, size, color, width_chars, a=1.0, anchor="lm", bold=False, lh=1.3):
    lines = textwrap.wrap(s, width_chars)
    n = len(lines)
    for k, ln in enumerate(lines):
        yy = y + (k - (n - 1) / 2) * size * lh
        cv.text(x, yy, ln, size, mix(cv.bg, color, a), anchor=anchor, bold=bold)


def arc(cv, x, y, r, frac, color, width=8):
    if frac <= 0:
        return
    cv.d.arc([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS],
             start=-90, end=-90 + 360 * frac, fill=color, width=int(width * SS))


def header(cv, t, eyebrow, title_parts, title_size=60, color=WHITE):
    if eyebrow:
        cv.text(W / 2, 70, eyebrow, 30, mix(BG, GREY, fade(t, 0)), bold=True)
    if title_parts:
        draw_formula(cv, W / 2, 135, title_parts if not isinstance(title_parts, str) else [(title_parts, color)],
                     title_size, a=fade(t, 0.1))


# --------------------------------------------------------------------------
# Escenas genéricas
# --------------------------------------------------------------------------
def free_scene(items, eyebrow=None, title=None, title_size=60):
    """Escena libre: lista de elementos que aparecen en su instante.

    ("f", t0, x, y, partes, tamaño[, align])        fórmula / texto con fórmulas
    ("t", t0, x, y, texto, tamaño, color[, bold, anchor, ancho])  texto
    ("arrow", t0, x0, y0, x1, y1[, color])
    ("box", t0, x0, y0, x1, y1[, color])            recuadro de fondo
    ("check", t0, x, y[, color])
    Si t0 es una tupla (t_in, t_out) el elemento desaparece en t_out.
    """
    def scene(cv, t, D):
        header(cv, t, eyebrow, title, title_size)
        for it in items:
            kind, t0 = it[0], it[1]
            t_out = None
            if isinstance(t0, tuple):
                t0, t_out = t0
            a = fade(t, t0, 0.5, t_out=t_out)
            if a <= 0:
                continue
            if kind == "f":
                _, _, x, y, parts, size, *rest = it
                draw_formula(cv, x, y, parts, size, a=a, align=rest[0] if rest else "center")
            elif kind == "t":
                _, _, x, y, s, size, col, *rest = it
                bold = rest[0] if len(rest) > 0 else False
                anchor = rest[1] if len(rest) > 1 else "mm"
                width = rest[2] if len(rest) > 2 else None
                if width:
                    wrap_text(cv, x, y, s, size, col, width, a=a, anchor=anchor, bold=bold)
                else:
                    cv.text(x, y, s, size, mix(BG, col, a), anchor=anchor, bold=bold)
            elif kind == "arrow":
                _, _, x0, y0, x1, y1, *rest = it
                col = rest[0] if rest else GREY
                cv.arrow(x0, y0, x0 + (x1 - x0) * ease((t - t0) / 0.5), y0 + (y1 - y0) * ease((t - t0) / 0.5),
                         mix(BG, col, a), width=7, head=26)
            elif kind == "box":
                _, _, x0, y0, x1, y1, *rest = it
                col = rest[0] if rest else PANEL
                cv.rect(x0, y0, x1, y1, fill=mix(BG, col, a), radius=18)
            elif kind == "check":
                _, _, x, y, *rest = it
                check_mark(cv, x, y, 50, mix(BG, rest[0] if rest else GREEN, a), w=10)
    return scene


def steps_scene(eyebrow, title, steps, title_size=64, wide=False):
    """Ejemplo resuelto paso a paso.

    steps: lista de (t0, explicación, fórmula[, destacado]).
    """
    def scene(cv, t, D):
        header(cv, t, eyebrow, title, title_size)
        n = len(steps)
        gap = 150 if n <= 4 else 125
        y0 = 300 if n <= 4 else 280
        for k, st in enumerate(steps):
            t0, label, parts = st[0], st[1], st[2]
            hl = len(st) > 3 and st[3]
            a = fade(t, t0)
            if a <= 0:
                continue
            y = y0 + k * gap
            if hl:
                cv.rect(140, y - 60, 1780, y + 60, fill=mix(BG, (22, 52, 40), a),
                        outline=mix(BG, GREEN, a), width=3, radius=18)
            cv.circle(200, y, 32, fill=mix(BG, GREEN if hl else YELLOW, a))
            if hl:
                check_mark(cv, 200, y, 30, mix(BG, BG, a), w=7)
            else:
                cv.text(200, y + 2, str(k + 1), 34, mix(BG, BG, a), bold=True)
            old = cv.bg
            if hl:
                cv.bg = mix(BG, (22, 52, 40), a)
            wrap_text(cv, 260, y, label, 33 if not wide else 38, WHITE if not hl else GREEN,
                      46 if not wide else 72, a=a, bold=hl)
            if parts:
                sz = fit(parts, 66 if not hl else 74, 620)
                draw_formula(cv, 1440, y, parts, sz, a=a)
            cv.bg = old
    return scene


def cross_scene(eyebrow, title, metal, mq, anion, aq, result, notes=(), times=None):
    """Cruce de cargas: la carga del catión pasa a ser el subíndice del anión
    y viceversa. `anion` son las partes de la fórmula del anión sin carga.

    Arriba se ven los iones con sus cargas; las flechas en X bajan a la
    fórmula cruzada (subíndices en amarillo) y abajo aparece el resultado."""
    tm = times or {"ions": 0.4, "arrows": 2.2, "subs": 3.4, "result": 5.2, "notes": 6.6}

    def qtxt(q, sign):
        return (f"{q}{sign}" if q > 1 else sign)

    aparts = _norm(anion)
    atoms = sum(1 for txt, _ in aparts for ch in txt if ch.isupper())
    paren = mq > 1 and atoms > 1
    crossed = [(metal, CAT)]
    if aq > 1:
        crossed.append((str(aq), OXN))
    if paren:
        crossed += [("(", AN)] + aparts + [(")", AN)]
    else:
        crossed += aparts
    if mq > 1:
        crossed.append((str(mq), OXN))

    def scene(cv, t, D):
        header(cv, t, eyebrow, title, 60)
        y = 300
        size = 110
        a = fade(t, tm["ions"])
        mparts = [(metal, CAT)]
        wm = formula_width(mparts, size)
        wa = formula_width(aparts, size)
        cm, ca = qtxt(mq, "+"), qtxt(aq, MINUS)
        csz = size * 0.55
        wcm = cv.text_width(cm, csz, True)
        wca = cv.text_width(ca, csz, True)
        gap = 300
        total = wm + wcm + gap + wa + wca
        xm = W / 2 - total / 2
        xa = xm + wm + wcm + gap
        draw_formula(cv, xm, y, mparts, size, a=a, align="left")
        draw_formula(cv, xa, y, aparts, size, a=a, align="left")
        hl = ramp(t, tm["arrows"] - 0.6, tm["arrows"])
        ccol = mix(WHITE, OXN, hl)
        cv.text(xm + wm + 4, y - size * 0.42, cm, csz, mix(BG, ccol, a), anchor="lm", bold=True)
        cv.text(xa + wa + 4, y - size * 0.42, ca, csz, mix(BG, ccol, a), anchor="lm", bold=True)
        # fórmula cruzada (fila de abajo) y posición de sus subíndices
        y2 = 560
        size2 = 96
        runs, w2 = formula_runs(crossed, size2)
        x2 = W / 2 - w2 / 2
        sub_m = sub_a = None
        end_m = x2 + formula_width([(metal, CAT)], size2)
        for txt, dx, dy, fs, col in runs:
            if col == OXN:
                cx = x2 + dx + cv.text_width(txt, fs, True) / 2
                if sub_m is None and aq > 1 and dx < end_m - x2 + 5:
                    sub_m = cx
                else:
                    sub_a = cx
        if sub_m is None:
            sub_m = end_m + 12
        if sub_a is None:
            sub_a = x2 + w2 + 12
        ysub = y2 + size2 * 0.2
        u = ramp(t, tm["arrows"], tm["arrows"] + 1.0)
        if u > 0:
            col = mix(BG, OXN, 0.85)
            p0 = (xm + wm + 4 + wcm / 2, y - size * 0.15)
            q0 = (xa + wa + 4 + wca / 2, y - size * 0.15)
            p1 = (sub_a, ysub - size2 * 0.45)
            q1 = (sub_m, ysub - size2 * 0.45)
            cv.arrow(p0[0], p0[1], p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u, col, width=6, head=24)
            cv.arrow(q0[0], q0[1], q0[0] + (q1[0] - q0[0]) * u, q0[1] + (q1[1] - q0[1]) * u, col, width=6, head=24)
        s = fade(t, tm["subs"])
        if s > 0:
            draw_formula(cv, x2, y2, crossed, size2, a=s, align="left")
            if aq == 1 or mq == 1:
                cv.text(W / 2, y2 + 95, "(el subíndice 1 no se escribe)", 30, mix(BG, GREY, s))
        r = fade(t, tm["result"])
        if r > 0:
            cv.rect(W / 2 - 400, 700, W / 2 + 400, 830, fill=mix(BG, (22, 52, 40), r),
                    outline=mix(BG, GREEN, r), width=3, radius=20)
            draw_formula(cv, W / 2, 765, result, fit(result, 90, 720), a=r, bg=mix(BG, (22, 52, 40), r))
        for k, nt in enumerate(notes):
            na = fade(t, tm["notes"] + k * 1.2)
            if na > 0:
                draw_formula(cv, W / 2, 880 + k * 50, nt, fit(nt, 36, 1600, False), a=na, bold=False)
    return scene


def table_scene(title, header_row, rows, col_x, t_rows=1.0, dt=0.35, row_h=60, y0=215, size=34,
                eyebrow=None, highlight_cols=()):
    def scene(cv, t, D):
        header(cv, t, eyebrow, title, 56)
        a = fade(t, 0.3)
        y = y0
        for x, h in zip(col_x, header_row):
            cv.text(x, y, h, 30, mix(BG, GREY, a), bold=True)
        cv.line([(col_x[0] - 230, y + 30), (col_x[-1] + 230, y + 30)], mix(BG, GRID, a), 3)
        for k, row in enumerate(rows):
            ra = fade(t, t_rows + k * dt)
            if ra <= 0:
                continue
            yy = y + 30 + row_h * (k + 0.75)
            if k % 2 == 0:
                cv.rect(col_x[0] - 230, yy - row_h / 2, col_x[-1] + 230, yy + row_h / 2,
                        fill=mix(BG, PANEL, ra), radius=8)
            old = cv.bg
            cv.bg = mix(BG, PANEL, ra) if k % 2 == 0 else BG
            for i, (x, cell) in enumerate(zip(col_x, row)):
                col = YELLOW if i in highlight_cols else WHITE
                parts = [(cell, col)] if isinstance(cell, str) else cell
                draw_formula(cv, x, yy, parts, size, a=ra, bold=(i in highlight_cols))
            cv.bg = old
    return scene


def practice_scene(n, kind, prompt, answer, explain=None, think=5.0):
    """Ejercicio: se muestra el enunciado, una cuenta atrás y la solución."""
    verb = "Formula" if kind == "formular" else "Nombra"

    def scene(cv, t, D):
        cv.text(W / 2, 75, f"PRACTICA · EJERCICIO {n}", 30, mix(BG, GREY, fade(t, 0)), bold=True)
        cv.text(W / 2, 200, verb + ":", 50, mix(BG, YELLOW, fade(t, 0.1)), bold=True)
        draw_formula(cv, W / 2, 330, prompt, fit(prompt, 92, 1600), a=fade(t, 0.3))
        t0, t1 = 1.0, 1.0 + think
        if t < t1 + 0.4:
            a = fade(t, t0, 0.4, t_out=t1, dur_out=0.4)
            frac = clamp((t - t0) / think)
            cv.circle(W / 2, 560, 70, outline=mix(BG, GRID, a), width=8)
            arc(cv, W / 2, 560, 70, frac, mix(BG, YELLOW, a), 8)
            left = max(0, math.ceil(t1 - t)) if t >= t0 else int(think)
            cv.text(W / 2, 562, str(left), 56, mix(BG, WHITE, a), bold=True)
            cv.text(W / 2, 690, "Pausa el vídeo si necesitas más tiempo", 34, mix(BG, GREY, a))
        r = fade(t, t1 + 0.2)
        if r > 0:
            cv.rect(W / 2 - 560, 480, W / 2 + 560, 650, fill=mix(BG, (22, 52, 40), r),
                    outline=mix(BG, GREEN, r), width=3, radius=20)
            draw_formula(cv, W / 2, 565, answer, fit(answer, 84, 1040), a=r, bg=mix(BG, (22, 52, 40), r))
            if explain:
                draw_formula(cv, W / 2, 735, explain, fit(explain, 38, 1700, False), a=fade(t, t1 + 0.8), bold=False)
    return scene


def title_scene(title, subtitle, level="1.º BACHILLERATO · FORMULACIÓN INORGÁNICA", deco=None):
    def scene(cv, t, D):
        cv.text(W / 2, 310, level, 32, mix(BG, GREY, fade(t, 0.2)), bold=True)
        cv.text(W / 2, 430, title, 110, mix(BG, WHITE, fade(t, 0.4, 0.8)), bold=True)
        cv.text(W / 2, 550, subtitle, 52, mix(BG, YELLOW, fade(t, 1.1, 0.8)))
        if deco:
            for k, parts in enumerate(deco):
                draw_formula(cv, W / 2 + (k - (len(deco) - 1) / 2) * 360, 720, parts, 64,
                             a=fade(t, 1.8 + 0.3 * k))
    return scene


def end_scene(title, subtitle):
    def scene(cv, t, D):
        cv.text(W / 2, H / 2 - 30, title, 80, mix(BG, WHITE, fade(t, 0.1, 0.6, D - 0.8, 0.6)), bold=True)
        cv.text(W / 2, H / 2 + 50, subtitle, 40, mix(BG, GREY, fade(t, 0.4, 0.6, D - 0.8, 0.6)))
    return scene


# --------------------------------------------------------------------------
# Render
# --------------------------------------------------------------------------
class Video:
    """Si existe `narracion.json` (lo crea `narrar.py --medir`) con la duración
    de cada frase hablada, cada tramo de narración se alarga lo necesario
    para que la voz quepa, y la animación de ese tramo va más despacio."""

    def __init__(self, scenes, here, out_name):
        self.here = here
        self.out_name = out_name
        durs = None
        jp = os.path.join(here, "narracion.json")
        if os.path.exists(jp):
            with open(jp, encoding="utf-8") as fh:
                durs = json.load(fh)["durs"]
        self.scenes = []   # (duración nueva, función, narración, mapa de tiempo)
        self.starts = []
        self.caps = []
        acc, k = 0.0, 0
        for d, f, caps in scenes:
            old = [0.0] + [c[0] for c in caps] + [d]
            new = [0.0, old[1] if caps else d]
            for i in range(len(caps)):
                seg = old[i + 2] - old[i + 1]
                if durs is not None:
                    seg = max(seg, durs[k + i] + 0.6)
                new.append(new[-1] + seg)
            dn = new[-1]
            self.starts.append(acc)
            self.scenes.append((dn, f, d, (new, old)))
            for i, c in enumerate(caps):
                t1 = new[i + 2] if i + 1 < len(caps) else dn - 0.2
                self.caps.append((acc + new[i + 1], acc + t1, c[1]) + ((c[2],) if len(c) > 2 else ()))
            k += len(caps)
            acc += dn
        self.total = acc

    @staticmethod
    def warp(t, maps):
        new, old = maps
        i = max(0, min(len(new) - 2, bisect.bisect_right(new, t) - 1))
        n0, n1, o0, o1 = new[i], new[i + 1], old[i], old[i + 1]
        if n1 <= n0:
            return o0
        return o0 + (t - n0) * (o1 - o0) / (n1 - n0)

    def draw_caption(self, cv, T):
        for c in self.caps:
            t0, t1, txt = c[0], c[1], c[2]
            if t0 <= T < t1:
                a = fade(T, t0, 0.25, t_out=t1 - 0.25, dur_out=0.25)
                lines = textwrap.wrap(txt, 64)
                hh = 50 * len(lines) + 30
                y0 = 1040 - hh
                cv.rect(160, y0, 1760, 1040, fill=mix(BG, (6, 9, 18), a), radius=14)
                for k, ln in enumerate(lines):
                    cv.text(W / 2, y0 + 40 + k * 50, ln, 36, mix((6, 9, 18), WHITE, a))
                break

    def render(self, T):
        cv = Canvas()
        for (d, f, d0, maps), s in zip(self.scenes, self.starts):
            if s <= T < s + d:
                f(cv, self.warp(T - s, maps), d0)
                break
        self.draw_caption(cv, T)
        cv.text(1885, 42, "@quantafyq", 30, mix(BG, WHITE, 0.6), anchor="rm", bold=True)
        img = cv.final()
        for s, (d, _, _, _) in zip(self.starts, self.scenes):
            if s <= T < s + d:
                t = T - s
                k = min(ramp(t, 0, 0.25), 1 - ramp(t, d - 0.25, d))
                if k < 1:
                    img = Image.blend(Image.new("RGB", img.size, BG), img, k)
                break
        return img

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
        ap.add_argument("--hd720", action="store_true")
        ap.add_argument("-o", "--output", default=os.path.join(self.here, self.out_name))
        args = ap.parse_args()
        if args.hd720:
            base.OUT_SCALE = 2 / 3
        print(f"Duración total: {self.total:.1f} s")
        if args.preview is not None:
            for s in args.preview:
                p = os.path.join(self.here, f"preview_{s:05.1f}.png")
                self.render(s).save(p)
                print("guardado", p)
            return
        srt = os.path.splitext(args.output)[0] + ".srt"
        self.write_srt(srt)
        nfr = int(self.total * FPS)
        ow, oh = int(W * base.OUT_SCALE), int(H * base.OUT_SCALE)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{ow}x{oh}", "-r", str(FPS), "-i", "-",
               "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
               "-movflags", "+faststart", args.output]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        global _VIDEO
        _VIDEO = self
        with mp.get_context("fork").Pool(os.cpu_count()) as pool:
            for k, buf in enumerate(pool.imap(_render_frame, range(nfr), chunksize=4)):
                proc.stdin.write(buf)
                if k % 600 == 0:
                    print(f"  fotograma {k}/{nfr}", flush=True)
        proc.stdin.close()
        proc.wait()
        print("vídeo:", args.output, "\nsubtítulos:", srt)


_VIDEO = None


def _render_frame(i):
    return _VIDEO.render(i / FPS).tobytes()
