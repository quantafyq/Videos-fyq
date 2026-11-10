#!/usr/bin/env python3
"""
Vídeo: «Sales ácidas: formular y nombrar» (1.º de Bachillerato).

Uso:
    python3 generar_video.py               # vídeo + subtítulos .srt
    python3 generar_video.py --preview 60  # PNG del segundo 60
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "comun"))
from formulacion import (  # noqa: E402
    Video, free_scene, steps_scene, cross_scene, table_scene, practice_scene,
    title_scene, end_scene, CAT, AN, HYD, WHITE, GREY, YELLOW, GREEN,
)

# --------------------------------------------------------------------------
# Escenas
# --------------------------------------------------------------------------
QUE_ES = free_scene([
    ("t", 0.5, 960, 215, "El ácido carbónico tiene 2 H", 36, GREY),
    # fila 1: se quitan todos los H -> sal neutra
    ("f", 3.5, 270, 360, [("H2", HYD), ("CO3", AN)], 76),
    ("t", 3.8, 500, 312, "quitamos 2 H", 28, YELLOW),
    ("arrow", 3.8, 410, 360, 590, 360, YELLOW),
    ("f", 4.4, 740, 360, [("CO3^2−", AN)], 76),
    ("arrow", 5.0, 880, 360, 1030, 360, GREY),
    ("f", 5.4, 1230, 360, [("Na2", CAT), ("CO3", AN)], 76),
    ("t", 5.8, 1620, 340, "carbonato de sodio", 32, WHITE, True),
    ("t", 5.8, 1620, 385, "sal neutra", 30, GREY),
    # fila 2: se quita una parte -> sal ácida
    ("f", 8.0, 270, 590, [("H2", HYD), ("CO3", AN)], 76),
    ("t", 8.3, 500, 542, "quitamos 1 H", 28, YELLOW),
    ("arrow", 8.3, 410, 590, 590, 590, YELLOW),
    ("f", 8.9, 740, 590, [("H", HYD), ("CO3^−", AN)], 76),
    ("arrow", 9.5, 880, 590, 1030, 590, GREY),
    ("f", 9.9, 1230, 590, [("Na", CAT), ("H", HYD), ("CO3", AN)], 76),
    ("t", 10.3, 1620, 570, "hidrogenocarbonato", 32, GREEN, True),
    ("t", 10.3, 1620, 612, "de sodio · sal ácida", 30, GREEN),
    ("box", 12.5, 230, 730, 1690, 850),
    ("t", 12.7, 960, 790, "Una sal ácida conserva algún H del ácido: solo la forman los ácidos con 2 o más H",
     34, WHITE, True),
], title="¿Qué es una sal ácida?")

NOMBRE = free_scene([
    ("box", 0.5, 360, 230, 1560, 370),
    ("t", 0.7, 960, 300, "hidrogeno + nombre del anión", 62, YELLOW, True),
    ("t", 2.2, 960, 420, "Se escribe todo junto", 36, GREY),
    ("f", 3.5, 700, 530, [("H", HYD), ("CO3^−", AN)], 72),
    ("arrow", 3.8, 860, 530, 1000, 530, GREY),
    ("t", 4.0, 1040, 530, "hidrogenocarbonato", 50, WHITE, True, "lm"),
    ("f", 6.0, 700, 660, [("H2", HYD), ("PO4^−", AN)], 72),
    ("arrow", 6.3, 860, 660, 1000, 660, GREY),
    ("t", 6.5, 1040, 660, "dihidrogenofosfato", 50, WHITE, True, "lm"),
    ("t", 7.5, 1040, 715, "si quedan 2 H: dihidrogeno", 30, YELLOW, False, "lm"),
    ("t", 10.0, 960, 830, "Nombres antiguos: bicarbonato de sodio, carbonato ácido de sodio", 34, GREY),
], title="El nombre de una sal ácida")

AN_ACIDOS = table_scene(
    "Los aniones ácidos más habituales",
    ["Ácido", "Anión ácido", "Nombre", "Carga"],
    [[[("H2", HYD), ("CO3", AN)], [("H", HYD), ("CO3^−", AN)], "hidrogenocarbonato", "1−"],
     [[("H2", HYD), ("SO4", AN)], [("H", HYD), ("SO4^−", AN)], "hidrogenosulfato", "1−"],
     [[("H2", HYD), ("SO3", AN)], [("H", HYD), ("SO3^−", AN)], "hidrogenosulfito", "1−"],
     [[("H3", HYD), ("PO4", AN)], [("H2", HYD), ("PO4^−", AN)], "dihidrogenofosfato", "1−"],
     [[("H3", HYD), ("PO4", AN)], [("H", HYD), ("PO4^2−", AN)], "hidrogenofosfato", "2−"],
     [[("H2", HYD), ("S", AN)], [("H", HYD), ("S^−", AN)], "hidrogenosulfuro", "1−"]],
    [430, 800, 1200, 1560], t_rows=1.0, dt=0.6, row_h=88, y0=220, size=40, highlight_cols=(3,))

METODO_F = steps_scene("FORMULAR", "Cómo formular una sal ácida", [
    (2.0, "Escribe el ácido de partida", []),
    (4.0, "Deja los H que indica el nombre (hidrogeno: 1 H, dihidrogeno: 2 H)", []),
    (6.5, "La carga del anión es igual al número de H que has quitado", []),
    (9.0, "Escribe el catión metálico y cruza las cargas", []),
], wide=True)

EJ1 = steps_scene("FORMULAR · EJEMPLO 1", "hidrogenocarbonato de sodio", [
    (1.0, "Carbonato viene del ácido carbónico", [("H2", HYD), ("CO3", AN)]),
    (3.5, "Le dejamos 1 H: hemos quitado 1 H, carga 1−", [("H", HYD), ("CO3^−", AN)]),
    (6.5, "El sodio tiene carga +1", [("Na^+", CAT)]),
    (9.0, "Las cargas +1 y 1− se compensan", [("Na", CAT), ("H", HYD), ("CO3", AN)], True),
])

EJ2 = steps_scene("FORMULAR · EJEMPLO 2", "dihidrogenofosfato de calcio", [
    (1.0, "Fosfato viene del ácido fosfórico", [("H3", HYD), ("PO4", AN)]),
    (3.5, "Le dejamos 2 H: hemos quitado 1 H, carga 1−", [("H2", HYD), ("PO4^−", AN)]),
    (6.5, "El calcio tiene carga 2+", [("Ca^2+", CAT)]),
])
EJ2X = cross_scene("FORMULAR · EJEMPLO 2", "dihidrogenofosfato de calcio", "Ca", 2, [("H2", HYD), ("PO4", AN)], 1,
                   [("Ca", CAT), ("(", AN), ("H2", HYD), ("PO4", AN), (")2", AN)],
                   notes=[[("El anión ácido va entre paréntesis porque lleva subíndice", WHITE)]])

EJ3 = steps_scene("FORMULAR · EJEMPLO 3", "hidrogenofosfato de sodio", [
    (1.0, "Fosfato viene del ácido fosfórico", [("H3", HYD), ("PO4", AN)]),
    (3.5, "Le dejamos 1 H: hemos quitado 2 H, carga 2−", [("H", HYD), ("PO4^2−", AN)]),
    (6.5, "El sodio tiene carga +1", [("Na^+", CAT)]),
])
EJ3X = cross_scene("FORMULAR · EJEMPLO 3", "hidrogenofosfato de sodio", "Na", 1, [("H", HYD), ("PO4", AN)], 2,
                   [("Na2", CAT), ("H", HYD), ("PO4", AN)],
                   notes=[[("El anión no lleva subíndice: no hacen falta paréntesis", WHITE)]])

METODO_N = steps_scene("NOMBRAR", "Cómo nombrar una sal ácida", [
    (2.0, "Separa el metal del anión ácido (el que lleva H)", []),
    (4.5, "Reconoce el anión: de qué ácido viene y cuántos H le quedan", []),
    (7.0, "Calcula la carga del metal para que el total sea cero", []),
    (9.5, "Nombre: (di)hidrogeno + anión + de + metal", []),
], wide=True)

N1 = steps_scene("NOMBRAR · EJEMPLO 1", [("K", CAT), ("H2", HYD), ("PO4", AN)], [
    (1.0, "Separamos metal y anión", [("K", CAT), ("   |   ", GREY), ("H2", HYD), ("PO4", AN)]),
    (3.5, "Viene del ácido fosfórico (H₃PO₄) y le quedan 2 H: dihidrogenofosfato, carga 1−",
     [("H2", HYD), ("PO4^−", AN)]),
    (7.0, "El potasio solo tiene una carga: +1", [("K^+", CAT)]),
    (10.0, "Sin número romano", [("dihidrogenofosfato de potasio", GREEN)], True),
], title_size=80)

N2 = steps_scene("NOMBRAR · EJEMPLO 2", [("Cu", CAT), ("(", AN), ("H", HYD), ("SO3", AN), (")2", AN)], [
    (1.0, "Separamos metal y anión", [("Cu", CAT), ("   |   ", GREY), ("(", AN), ("H", HYD), ("SO3", AN), (")2", AN)]),
    (3.5, "Viene del ácido sulfuroso (H₂SO₃) y le queda 1 H: hidrogenosulfito, carga 1−",
     [("H", HYD), ("SO3^−", AN)]),
    (7.0, "Hay 2 aniones: 2 · (1−) = 2−, así que el cobre es 2+", [("Cu^2+", CAT)]),
    (10.0, "El cobre puede ser +1 o +2", [("hidrogenosulfito de cobre(II)", GREEN)], True),
], title_size=80)

P1 = practice_scene(1, "formular", [("hidrogenocarbonato de magnesio", WHITE)],
                    [("Mg", CAT), ("(", AN), ("H", HYD), ("CO3", AN), (")2", AN)],
                    [("H", HYD), ("CO3^−", AN), ("  (de H2CO3, quitamos 1 H)      magnesio  →  ", GREY), ("Mg^2+", CAT)])
P2 = practice_scene(2, "nombrar", [("Na", CAT), ("H", HYD), ("SO4", AN)], [("hidrogenosulfato de sodio", GREEN)],
                    [("H", HYD), ("SO4^−", AN), (" viene del ácido sulfúrico (H2SO4) y le queda 1 H", GREY)])
P3 = practice_scene(3, "formular", [("hidrogenofosfato de potasio", WHITE)],
                    [("K2", CAT), ("H", HYD), ("PO4", AN)],
                    [("H", HYD), ("PO4^2−", AN), ("  (de H3PO4, quitamos 2 H)      potasio  →  ", GREY), ("K^+", CAT)])
P4 = practice_scene(4, "nombrar", [("Fe", CAT), ("(", AN), ("H", HYD), ("CO3", AN), (")3", AN)],
                    [("hidrogenocarbonato de hierro(III)", GREEN)],
                    [("3 aniones ", GREY), ("H", HYD), ("CO3^−", AN), (": 3 · (1−) = 3−, así que el hierro es 3+", GREY)])

RESUMEN = free_scene(
    [("check", 0.8 + 1.5 * k, 250, 260 + 125 * k) for k in range(5)] +
    [("t", 0.8 + 1.5 * k, 310, 260 + 125 * k, s, 40, WHITE, True, "lm") for k, s in enumerate([
        "Sal ácida: el anión conserva algún H del ácido",
        "Solo la forman los ácidos con 2 o más H",
        "Nombre: hidrogeno / dihidrogeno + anión + de + metal",
        "Carga del anión = n.º de H que se han quitado",
        "En la fórmula el H va delante del anión: NaHCO₃",
    ])],
    title="En resumen", title_size=70)

# --------------------------------------------------------------------------
# Guion
# --------------------------------------------------------------------------
SCENES = [
    (6.0, title_scene("Sales ácidas", "Formular y nombrar",
                      deco=[[("Na", CAT), ("H", HYD), ("CO3", AN)], [("K", CAT), ("H", HYD), ("SO4", AN)],
                            [("Ca", CAT), ("(", AN), ("H2", HYD), ("PO4", AN), (")2", AN)]]), [
        (1.2, "En este vídeo vas a aprender a formular y a nombrar sales ácidas.")]),
    (17.0, QUE_ES, [
        (0.3, "El ácido carbónico, H₂CO₃, tiene dos hidrógenos.", "El ácido carbónico, hache dos, ce, o tres, tiene dos hidrógenos."),
        (3.5, "Si le quitamos los dos, obtenemos el anión carbonato y una sal neutra: el carbonato de sodio."),
        (8.0, "Pero si solo le quitamos uno, el anión conserva un hidrógeno: es una sal ácida, el hidrogenocarbonato de sodio."),
        (12.5, "Por eso solo pueden formar sales ácidas los ácidos que tienen dos o más hidrógenos.")]),
    (14.0, NOMBRE, [
        (0.3, "Para nombrarlas se pone la palabra hidrogeno delante del nombre del anión, todo junto.",
         "Para nombrarlas se pone la palabra hidrógeno delante del nombre del anión, todo junto."),
        (3.5, "Por ejemplo, HCO₃⁻ es el hidrogenocarbonato.", "Por ejemplo, hache ce o tres menos es el hidrogenocarbonato."),
        (6.0, "Si quedan dos hidrógenos se dice dihidrogeno: dihidrogenofosfato.",
         "Si quedan dos hidrógenos se dice dihidrógeno: dihidrogenofosfato."),
        (10.0, "Quizá conozcas nombres antiguos como bicarbonato o carbonato ácido, pero hoy se usa hidrogenocarbonato.")]),
    (15.0, AN_ACIDOS, [
        (0.3, "Estos son los aniones ácidos más habituales."),
        (4.5, "Fíjate en la carga: es igual al número de hidrógenos que se han quitado al ácido."),
        (9.0, "Del ácido fosfórico salen dos: el dihidrogenofosfato, con carga 1−, y el hidrogenofosfato, con carga 2−.",
         "Del ácido fosfórico salen dos: el dihidrogenofosfato, con una carga negativa, y el hidrogenofosfato, con dos."),
        (13.0, "El H₂S no es un oxoácido, pero también forma sales ácidas.", "El ácido sulfhídrico no es un oxoácido, pero también forma sales ácidas.")]),
    (12.5, METODO_F, [
        (0.3, "Para formular una sal ácida:"),
        (2.0, "escribe el ácido de partida,"),
        (4.0, "déjale los hidrógenos que indica el nombre,"),
        (6.5, "recuerda que la carga del anión es igual al número de hidrógenos que has quitado,"),
        (9.0, "y escribe el catión metálico y cruza las cargas, como en las oxisales.")]),
    (13.0, EJ1, [
        (0.3, "Primer ejemplo: hidrogenocarbonato de sodio."),
        (1.0, "Viene del ácido carbónico, que tiene dos hidrógenos."),
        (3.5, "Le dejamos uno, así que hemos quitado un hidrógeno: el anión tiene una carga negativa."),
        (6.5, "El sodio forma el catión Na⁺.", "El sodio forma el catión ene a más."),
        (9.0, "Las cargas se compensan: NaHCO₃. Es el bicarbonato que tienes en la cocina.",
         "Las cargas se compensan: ene a, hache, ce, o tres. Es el bicarbonato que tienes en la cocina.")]),
    (9.5, EJ2, [
        (0.3, "Segundo ejemplo: dihidrogenofosfato de calcio."),
        (1.0, "Viene del ácido fosfórico, H₃PO₄, con tres hidrógenos.", "Viene del ácido fosfórico, hache tres, pe, o cuatro, con tres hidrógenos."),
        (3.5, "Le dejamos dos, así que hemos quitado uno: carga 1−.", "Le dejamos dos, así que hemos quitado uno: una carga negativa."),
        (6.5, "El calcio tiene carga 2+.", "El calcio tiene carga dos más.")]),
    (11.0, EJ2X, [
        (0.3, "Cruzamos las cargas: el 2 del calcio pasa al anión y el 1 del anión pasa al calcio.",
         "Cruzamos las cargas: el dos del calcio pasa al anión, y el uno del anión pasa al calcio."),
        (5.2, "Resultado: Ca(H₂PO₄)₂. El anión va entre paréntesis porque lleva subíndice.",
         "Resultado: ce a, hache dos pe o cuatro entre paréntesis, dos. El anión va entre paréntesis porque lleva subíndice.")]),
    (9.5, EJ3, [
        (0.3, "Tercer ejemplo: hidrogenofosfato de sodio."),
        (1.0, "También viene del ácido fosfórico."),
        (3.5, "Ahora le dejamos un solo hidrógeno: hemos quitado dos, así que la carga es 2−.",
         "Ahora le dejamos un solo hidrógeno: hemos quitado dos, así que tiene dos cargas negativas."),
        (6.5, "El sodio tiene carga +1.", "El sodio tiene carga más uno.")]),
    (11.0, EJ3X, [
        (0.3, "Al cruzar las cargas, el sodio lleva un 2 y el anión un 1, que no se escribe.",
         "Al cruzar las cargas, el sodio lleva un dos y el anión un uno, que no se escribe."),
        (5.2, "Resultado: Na₂HPO₄, sin paréntesis.", "Resultado: ene a dos, hache, pe, o cuatro, sin paréntesis.")]),
    (13.0, METODO_N, [
        (0.3, "Para nombrar una sal ácida:"),
        (2.0, "separa el metal del anión, que es el que lleva el hidrógeno,"),
        (4.5, "reconoce de qué ácido viene y cuántos hidrógenos le quedan,"),
        (7.0, "calcula la carga del metal para que el compuesto sea neutro,"),
        (9.5, "y di hidrogeno o dihidrogeno, el anión, «de» y el metal.",
         "y di hidrógeno o dihidrógeno, el anión, de, y el metal.")]),
    (14.0, N1, [
        (0.3, "Vamos a nombrar KH₂PO₄.", "Vamos a nombrar ka, hache dos, pe, o cuatro."),
        (1.0, "Separamos el potasio del anión H₂PO₄.", "Separamos el potasio del anión hache dos pe o cuatro."),
        (3.5, "Viene del ácido fosfórico y le quedan dos hidrógenos: es el dihidrogenofosfato, con una carga negativa."),
        (7.0, "El potasio solo puede tener carga +1.", "El potasio solo puede tener carga más uno."),
        (10.0, "Nombre: dihidrogenofosfato de potasio, sin número romano.")]),
    (14.0, N2, [
        (0.3, "Otro ejemplo: Cu(HSO₃)₂.", "Otro ejemplo: ce u, hache ese o tres entre paréntesis, dos."),
        (1.0, "Separamos el cobre del anión HSO₃.", "Separamos el cobre del anión hache ese o tres."),
        (3.5, "Viene del ácido sulfuroso y le queda un hidrógeno: es el hidrogenosulfito, con carga 1−.",
         "Viene del ácido sulfuroso y le queda un hidrógeno: es el hidrogenosulfito, con una carga negativa."),
        (7.0, "Hay dos aniones, que suman dos cargas negativas, así que el cobre es 2+.",
         "Hay dos aniones, que suman dos cargas negativas, así que el cobre es dos más."),
        (10.0, "Nombre: hidrogenosulfito de cobre(II).", "Nombre: hidrogenosulfito de cobre dos.")]),
    (11.0, P1, [
        (0.3, "Ahora practica tú. Formula el hidrogenocarbonato de magnesio."),
        (6.2, "Solución: Mg(HCO₃)₂.", "Solución: eme ge, hache ce o tres entre paréntesis, dos.")]),
    (11.0, P2, [
        (0.3, "Nombra NaHSO₄.", "Nombra ene a, hache, ese, o cuatro."),
        (6.2, "Solución: hidrogenosulfato de sodio.")]),
    (11.0, P3, [
        (0.3, "Formula el hidrogenofosfato de potasio."),
        (6.2, "Solución: K₂HPO₄.", "Solución: ka dos, hache, pe, o cuatro.")]),
    (11.0, P4, [
        (0.3, "Nombra Fe(HCO₃)₃.", "Nombra efe e, hache ce o tres entre paréntesis, tres."),
        (6.2, "Solución: hidrogenocarbonato de hierro(III).", "Solución: hidrogenocarbonato de hierro tres.")]),
    (13.5, RESUMEN, [
        (0.3, "En resumen: en una sal ácida el anión conserva algún hidrógeno del ácido."),
        (3.8, "Se nombran con hidrogeno o dihidrogeno delante del anión.",
         "Se nombran con hidrógeno o dihidrógeno delante del anión."),
        (6.8, "La carga del anión es igual al número de hidrógenos que se han quitado,"),
        (9.8, "y en la fórmula el hidrógeno se escribe delante del anión.")]),
    (4.0, end_scene("Sales ácidas", "@quantafyq · Física y Química"), []),
]

VIDEO = Video(SCENES, HERE, "sales_acidas.mp4")
CAPS, TOTAL = VIDEO.caps, VIDEO.total

if __name__ == "__main__":
    VIDEO.main()
