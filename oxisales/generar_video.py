#!/usr/bin/env python3
"""
Vídeo: «Oxisales: formular y nombrar» (1.º de Bachillerato).

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
    title_scene, end_scene, CAT, AN, HYD, WHITE, GREY, YELLOW, GREEN, W,
)

# --------------------------------------------------------------------------
# Escenas
# --------------------------------------------------------------------------
INTRO = free_scene([
    ("f", 0.5, 470, 330, [("H2", HYD), ("SO4", AN)], 120),
    ("t", 0.8, 470, 440, "ácido sulfúrico", 36, GREY),
    ("t", 1.0, 470, 492, "OXOÁCIDO", 30, HYD, True),
    ("arrow", 3.0, 720, 330, 1200, 330, YELLOW),
    ("t", 3.2, 960, 392, "los H se sustituyen por un metal", 28, YELLOW),
    ("f", 3.6, 1450, 330, [("Cu", CAT), ("SO4", AN)], 120),
    ("t", 3.9, 1450, 440, "sulfato de cobre(II)", 36, GREY),
    ("t", 4.1, 1450, 492, "OXISAL", 30, CAT, True),
    ("box", 7.0, 330, 600, 1590, 810),
    ("t", 7.2, 960, 660, "Oxisal = metal + no metal + oxígeno", 50, WHITE, True),
    ("f", 11.0, 960, 750, [("catión metálico ", GREY), ("(Cu^2+)", CAT), ("  +  anión del oxoácido ", GREY),
                            ("(SO4^2−)", AN)], 36),
], title="¿Qué es una oxisal?")

ACIDOS = table_scene(
    "Recuerda: los oxoácidos",
    ["N.º de oxidación del Cl", "Prefijo y sufijo", "Fórmula", "Ácido"],
    [["+1", "hipo– … –oso", [("H", HYD), ("ClO", AN)], "hipocloroso"],
     ["+3", "… –oso", [("H", HYD), ("ClO2", AN)], "cloroso"],
     ["+5", "… –ico", [("H", HYD), ("ClO3", AN)], "clórico"],
     ["+7", "per– … –ico", [("H", HYD), ("ClO4", AN)], "perclórico"]],
    [400, 820, 1200, 1580], t_rows=3.5, dt=1.4, row_h=105, y0=260, size=44, highlight_cols=(0,))

TERMINACIONES = free_scene([
    ("t", 1.5, 760, 320, "–oso", 96, HYD, True),
    ("arrow", 1.9, 920, 320, 1060, 320, YELLOW),
    ("t", 2.3, 1180, 320, "–ito", 96, AN, True),
    ("t", 3.6, 760, 480, "–ico", 96, HYD, True),
    ("arrow", 4.0, 920, 480, 1060, 480, YELLOW),
    ("t", 4.4, 1180, 480, "–ato", 96, AN, True),
    ("box", 5.6, 260, 590, 1660, 700),
    ("t", 5.8, 960, 645, "«Cuando el OSO toca el pITO, PeriCO toca el silbATO»", 42, YELLOW, True),
    ("t", 9.0, 960, 790, "Los prefijos hipo– y per– se mantienen: hipoclorito, perclorato", 38, WHITE),
], title="Del ácido al anión: cambia la terminación")

ROWS = [
    ("hipocloroso", "H", "ClO", "", "hipoclorito", "−"),
    ("cloroso", "H", "ClO2", "", "clorito", "−"),
    ("clórico", "H", "ClO3", "", "clorato", "−"),
    ("perclórico", "H", "ClO4", "", "perclorato", "−"),
    ("sulfuroso", "H2", "SO3", "2", "sulfito", "2−"),
    ("sulfúrico", "H2", "SO4", "2", "sulfato", "2−"),
    ("nitroso", "H", "NO2", "", "nitrito", "−"),
    ("nítrico", "H", "NO3", "", "nitrato", "−"),
    ("carbónico", "H2", "CO3", "2", "carbonato", "2−"),
    ("fosfórico", "H3", "PO4", "3", "fosfato", "3−"),
    ("permangánico", "H", "MnO4", "", "permanganato", "−"),
]
ANIONES = table_scene(
    "Los aniones más habituales",
    ["Ácido", "Fórmula", "Anión", "Nombre del anión"],
    [[r[0], [(r[1], HYD), (r[2], AN)], [(r[2] + "^" + r[5], AN)], r[4]] for r in ROWS],
    [430, 820, 1160, 1530], t_rows=1.0, dt=0.35, row_h=58, y0=200, size=32)

METODO_F = steps_scene("FORMULAR", "Cómo formular una oxisal", [
    (2.0, "Escribe el oxoácido del que procede (–ito → –oso, –ato → –ico)", []),
    (4.5, "Quita los H: el anión tiene tantas cargas negativas como H has quitado", []),
    (7.0, "Escribe el catión metálico con su carga (el número romano te la da)", []),
    (9.5, "Cruza las cargas como subíndices y simplifica si se puede", []),
], wide=True)

EJ1 = steps_scene("FORMULAR · EJEMPLO 1", "nitrato de potasio", [
    (1.0, "–ato viene de –ico: ácido nítrico", [("H", HYD), ("NO3", AN)]),
    (3.5, "Quitamos 1 H: el anión tiene carga 1−", [("NO3^−", AN)]),
    (6.0, "El potasio solo tiene una carga: +1", [("K^+", CAT)]),
    (8.5, "Las cargas +1 y 1− se compensan", [("K", CAT), ("NO3", AN)], True),
])

EJ2 = steps_scene("FORMULAR · EJEMPLO 2", "sulfato de hierro(III)", [
    (1.0, "–ato viene de –ico: ácido sulfúrico", [("H2", HYD), ("SO4", AN)]),
    (3.5, "Quitamos 2 H: el anión tiene carga 2−", [("SO4^2−", AN)]),
    (6.0, "Hierro(III): el catión tiene carga 3+", [("Fe^3+", CAT)]),
])
EJ2X = cross_scene("FORMULAR · EJEMPLO 2", "sulfato de hierro(III)", "Fe", 3, [("SO4", AN)], 2,
                   [("Fe2", CAT), ("(SO4)3", AN)],
                   notes=[[("El anión va entre paréntesis porque lleva subíndice", WHITE)]])

EJ3 = steps_scene("FORMULAR · EJEMPLO 3", "carbonato de calcio", [
    (1.0, "–ato viene de –ico: ácido carbónico", [("H2", HYD), ("CO3", AN)]),
    (3.0, "Quitamos 2 H: el anión tiene carga 2−", [("CO3^2−", AN)]),
    (5.0, "El calcio tiene carga 2+", [("Ca^2+", CAT)]),
])
EJ3X = cross_scene("FORMULAR · EJEMPLO 3", "carbonato de calcio", "Ca", 2, [("CO3", AN)], 2,
                   [("Ca", CAT), ("CO3", AN)],
                   notes=[[("Los subíndices 2 y 2 se simplifican. Los de dentro del anión nunca cambian", WHITE)]])

METODO_N = steps_scene("NOMBRAR", "Cómo nombrar una oxisal", [
    (2.0, "Separa el metal del anión", []),
    (4.5, "Reconoce el anión: busca su ácido y cambia –oso → –ito, –ico → –ato", []),
    (7.0, "Calcula la carga del metal para que el total sea cero", []),
    (9.5, "Nombre: anión + «de» + metal (con número romano si tiene varias cargas)", []),
], wide=True)

N1 = steps_scene("NOMBRAR · EJEMPLO 1", [("Cu", CAT), ("SO4", AN)], [
    (1.0, "Separamos metal y anión", [("Cu", CAT), ("   |   ", GREY), ("SO4", AN)]),
    (3.5, "SO₄ viene del ácido sulfúrico (H₂SO₄): es el sulfato, con carga 2−", [("SO4^2−", AN)]),
    (7.0, "Para que el total sea cero, el cobre tiene carga 2+", [("Cu^2+", CAT)]),
    (10.0, "El cobre puede ser +1 o +2: lo indicamos", [("sulfato de cobre(II)", GREEN)], True),
], title_size=80)

N2 = steps_scene("NOMBRAR · EJEMPLO 2", [("Fe", CAT), ("(NO2)2", AN)], [
    (1.0, "Separamos metal y anión", [("Fe", CAT), ("   |   ", GREY), ("(NO2)2", AN)]),
    (3.5, "NO₂ viene del ácido nitroso (HNO₂): es el nitrito, con carga 1−", [("NO2^−", AN)]),
    (7.0, "Hay 2 nitritos: 2 · (1−) = 2−, así que el hierro es 2+", [("Fe^2+", CAT)]),
    (10.0, "El hierro puede ser +2 o +3: lo indicamos", [("nitrito de hierro(II)", GREEN)], True),
], title_size=80)

P1 = practice_scene(1, "formular", [("clorato de potasio", WHITE)], [("K", CAT), ("ClO3", AN)],
                    [("ácido clórico HClO3  →  ", GREY), ("ClO3^−", AN), ("      potasio  →  ", GREY), ("K^+", CAT)])
P2 = practice_scene(2, "nombrar", [("Al2", CAT), ("(SO4)3", AN)], [("sulfato de aluminio", GREEN)],
                    [("SO4^2−", AN), (" es el sulfato · el aluminio solo tiene una carga (3+): sin número romano", GREY)])
P3 = practice_scene(3, "formular", [("hipoclorito de sodio", WHITE)], [("Na", CAT), ("ClO", AN)],
                    [("ácido hipocloroso HClO  →  ", GREY), ("ClO^−", AN), ("      sodio  →  ", GREY), ("Na^+", CAT),
                     ("      (¡es la lejía!)", GREY)])
P4 = practice_scene(4, "nombrar", [("Ca3", CAT), ("(PO4)2", AN)], [("fosfato de calcio", GREEN)],
                    [("PO4^3−", AN), (" viene del ácido fosfórico (H3PO4) · el calcio solo tiene una carga (2+)", GREY)])

RESUMEN = free_scene(
    [("check", 0.8 + 1.4 * k, 250, 250 + 120 * k) for k in range(5)] +
    [("t", 0.8 + 1.4 * k, 310, 250 + 120 * k, s, 40, WHITE, True, "lm") for k, s in enumerate([
        "Oxisal = catión metálico + anión del oxoácido",
        "–oso → –ito   ·   –ico → –ato   (hipo– y per– se mantienen)",
        "Carga del anión = n.º de H que ha perdido el ácido",
        "Cruza las cargas, usa paréntesis si hace falta y simplifica",
        "Nombre: anión + de + metal (número romano si tiene varias cargas)",
    ])],
    title="En resumen", title_size=70)

# --------------------------------------------------------------------------
# Guion: (duración, escena, narración [(t, texto, texto hablado opcional)])
# --------------------------------------------------------------------------
SCENES = [
    (6.0, title_scene("Oxisales", "Formular y nombrar",
                      deco=[[("K", CAT), ("NO3", AN)], [("Cu", CAT), ("SO4", AN)], [("Na", CAT), ("ClO", AN)]]), [
        (1.2, "En este vídeo vas a aprender a formular y a nombrar oxisales.")]),
    (16.0, INTRO, [
        (0.3, "Una oxisal se obtiene a partir de un oxoácido, como el ácido sulfúrico."),
        (3.0, "Si sustituimos sus hidrógenos por un metal, obtenemos una oxisal: el sulfato de cobre(II).",
         "Si sustituimos sus hidrógenos por un metal, obtenemos una oxisal: el sulfato de cobre dos."),
        (7.0, "Las oxisales tienen tres elementos: un metal, un no metal y oxígeno."),
        (11.0, "Están formadas por un catión metálico y el anión que procede del oxoácido.")]),
    (15.0, ACIDOS, [
        (0.3, "Para formular una oxisal primero tienes que saber de qué oxoácido procede."),
        (3.5, "El nombre del ácido depende del número de oxidación del no metal: hipo…oso, …oso, …ico y per…ico, de menor a mayor.",
         "El nombre del ácido depende del número de oxidación del no metal: hipo oso, oso, ico y per ico, de menor a mayor."),
        (10.0, "Si el no metal solo tiene dos números de oxidación, se usan …oso para el menor e …ico para el mayor.",
         "Si el no metal solo tiene dos números de oxidación, se usa oso para el menor e ico para el mayor.")]),
    (13.0, TERMINACIONES, [
        (0.3, "Al quitarle los hidrógenos al ácido obtenemos el anión, que cambia de terminación."),
        (2.0, "La terminación –oso pasa a –ito, y la terminación –ico pasa a –ato.",
         "La terminación oso pasa a ito, y la terminación ico pasa a ato."),
        (5.6, "Un truco para recordarlo: «cuando el oso toca el pito, Perico toca el silbato».",
         "Un truco para recordarlo: cuando el oso toca el pito, Perico toca el silbato."),
        (9.0, "Los prefijos hipo– y per– se mantienen: hipoclorito, perclorato.",
         "Los prefijos hipo y per se mantienen: hipoclorito, perclorato.")]),
    (18.0, ANIONES, [
        (0.3, "Estos son los aniones más habituales. Fíjate en su carga:"),
        (4.5, "el anión tiene tantas cargas negativas como hidrógenos ha perdido el ácido."),
        (9.0, "Por ejemplo, el ácido sulfúrico tiene dos H, así que el sulfato tiene carga 2−.",
         "Por ejemplo, el ácido sulfúrico tiene dos hidrógenos, así que el sulfato tiene dos cargas negativas."),
        (13.5, "El bromo y el yodo forman ácidos y aniones iguales que los del cloro: bromato, yodato…",
         "El bromo y el yodo forman ácidos y aniones iguales que los del cloro: bromato, yodato.")]),
    (13.0, METODO_F, [
        (0.3, "Para formular una oxisal sigue cuatro pasos."),
        (2.0, "Uno: escribe el oxoácido del que procede."),
        (4.5, "Dos: quítale los hidrógenos para obtener el anión."),
        (7.0, "Tres: escribe el catión metálico con su carga."),
        (9.5, "Y cuatro: cruza las cargas y simplifica si se puede.")]),
    (13.0, EJ1, [
        (0.3, "Primer ejemplo: nitrato de potasio."),
        (1.0, "Nitrato viene del ácido nítrico, HNO₃.", "Nitrato viene del ácido nítrico, hache, ene, o tres."),
        (3.5, "Al quitarle su único hidrógeno queda el anión nitrato, con una carga negativa."),
        (6.0, "El potasio forma el catión K⁺.", "El potasio forma el catión ka más."),
        (8.5, "Las cargas se compensan una a una: la fórmula es KNO₃.",
         "Las cargas se compensan una a una: la fórmula es ka, ene, o tres.")]),
    (9.0, EJ2, [
        (0.3, "Segundo ejemplo: sulfato de hierro(III).", "Segundo ejemplo: sulfato de hierro tres."),
        (1.0, "Sulfato viene del ácido sulfúrico, H₂SO₄.", "Sulfato viene del ácido sulfúrico, hache dos, ese, o cuatro."),
        (3.5, "Al quitarle sus dos hidrógenos, el sulfato queda con dos cargas negativas."),
        (6.0, "El número romano nos dice que el hierro tiene carga 3+.",
         "El número romano nos dice que el hierro tiene carga tres más.")]),
    (11.0, EJ2X, [
        (0.3, "Ahora cruzamos las cargas: el 3 del hierro pasa al sulfato y el 2 del sulfato pasa al hierro.",
         "Ahora cruzamos las cargas: el tres del hierro pasa al sulfato, y el dos del sulfato pasa al hierro."),
        (5.2, "Resultado: Fe₂(SO₄)₃. El sulfato va entre paréntesis porque lleva subíndice.",
         "Resultado: efe e dos, ese o cuatro entre paréntesis, tres. El sulfato va entre paréntesis porque lleva subíndice.")]),
    (8.0, EJ3, [
        (0.3, "Tercer ejemplo: carbonato de calcio."),
        (1.0, "Viene del ácido carbónico, H₂CO₃, así que el carbonato tiene dos cargas negativas.",
         "Viene del ácido carbónico, hache dos, ce, o tres, así que el carbonato tiene dos cargas negativas."),
        (5.0, "El calcio forma el catión Ca²⁺.", "El calcio forma el catión calcio dos más.")]),
    (12.0, EJ3X, [
        (0.3, "Al cruzar las cargas nos queda un dos en cada lado.",),
        (5.2, "Como los subíndices son iguales, se simplifican: la fórmula es CaCO₃.",
         "Como los subíndices son iguales, se simplifican: la fórmula es ce a, ce, o tres."),
        (8.5, "Ojo: solo se simplifican los subíndices de fuera. Los del anión nunca cambian.")]),
    (13.0, METODO_N, [
        (0.3, "Para nombrar una oxisal hacemos el camino inverso."),
        (2.0, "Separa el metal del anión,"),
        (4.5, "reconoce el anión a partir de su ácido,"),
        (7.0, "calcula la carga del metal para que el compuesto sea neutro"),
        (9.5, "y di primero el nombre del anión, después «de» y el nombre del metal.",
         "y di primero el nombre del anión, después de, y el nombre del metal.")]),
    (14.0, N1, [
        (0.3, "Vamos a nombrar CuSO₄.", "Vamos a nombrar ce u, ese, o cuatro."),
        (1.0, "Separamos el metal, el cobre, del anión SO₄.", "Separamos el metal, el cobre, del anión ese o cuatro."),
        (3.5, "SO₄ procede del ácido sulfúrico: es el anión sulfato, con dos cargas negativas.",
         "Ese o cuatro procede del ácido sulfúrico: es el anión sulfato, con dos cargas negativas."),
        (7.0, "Para que el compuesto sea neutro, el cobre tiene que tener carga 2+.",
         "Para que el compuesto sea neutro, el cobre tiene que tener carga dos más."),
        (10.0, "Como el cobre puede actuar con +1 o +2, lo indicamos: sulfato de cobre(II).",
         "Como el cobre puede actuar con más uno o más dos, lo indicamos: sulfato de cobre dos.")]),
    (14.0, N2, [
        (0.3, "Otro ejemplo: Fe(NO₂)₂.", "Otro ejemplo: efe e, ene o dos entre paréntesis, dos."),
        (1.0, "Separamos el hierro del anión NO₂.", "Separamos el hierro del anión ene o dos."),
        (3.5, "NO₂ procede del ácido nitroso: es el anión nitrito, con una carga negativa.",
         "Ene o dos procede del ácido nitroso: es el anión nitrito, con una carga negativa."),
        (7.0, "Hay dos nitritos, que suman dos cargas negativas, así que el hierro es 2+.",
         "Hay dos nitritos, que suman dos cargas negativas, así que el hierro es dos más."),
        (10.0, "El nombre es nitrito de hierro(II).", "El nombre es nitrito de hierro dos.")]),
    (11.0, P1, [
        (0.3, "Ahora practica tú. Formula el clorato de potasio."),
        (6.2, "Solución: KClO₃.", "Solución: ka, ce ele, o tres.")]),
    (11.0, P2, [
        (0.3, "Nombra Al₂(SO₄)₃.", "Nombra a ele dos, ese o cuatro entre paréntesis, tres."),
        (6.2, "Solución: sulfato de aluminio. El aluminio solo tiene una carga, así que no lleva número romano.")]),
    (11.0, P3, [
        (0.3, "Formula el hipoclorito de sodio."),
        (6.2, "Solución: NaClO. Es el componente principal de la lejía.",
         "Solución: ene a, ce ele, o. Es el componente principal de la lejía.")]),
    (11.0, P4, [
        (0.3, "Nombra Ca₃(PO₄)₂.", "Nombra ce a tres, pe o cuatro entre paréntesis, dos."),
        (6.2, "Solución: fosfato de calcio.")]),
    (13.0, RESUMEN, [
        (0.3, "En resumen: una oxisal está formada por un catión metálico y el anión de un oxoácido."),
        (3.5, "Al pasar del ácido al anión, oso cambia a ito e ico cambia a ato."),
        (6.5, "La carga del anión es igual al número de hidrógenos que ha perdido el ácido."),
        (9.3, "Cruza las cargas para formular, y para nombrar di el anión, «de» y el metal.",
         "Cruza las cargas para formular, y para nombrar di el anión, de, y el metal.")]),
    (4.0, end_scene("Oxisales", "@quantafyq · Física y Química"), []),
]

VIDEO = Video(SCENES, HERE, "oxisales.mp4")
CAPS, TOTAL = VIDEO.caps, VIDEO.total

if __name__ == "__main__":
    VIDEO.main()
