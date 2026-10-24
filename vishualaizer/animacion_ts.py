
"""
Animación con Manim de Tabú Search para el TSP con camión y dron.

No reemplaza a visualizador.py: este archivo es independiente.

Qué muestra:
  1. Los nodos, distinguiendo clientes que pueden ser atendidos por dron y los que no.
  2. La solución inicial del camión (vecino más cercano).
  3. Por cada iteración de TS: los vecinos que se generan uno por uno, la selección del mejor,
     el agregado del vuelo del dron a la ruta, la inserción en la lista tabú y cuánto
     cambia el makespan.
  4. Se repite hasta que no quedan vecinos válidos. Al final se entrega la mejor solución.

Cómo se obtienen los pasos: el algoritmo NO se reimplementa aquí. El script compila (si hace
falta) y ejecuta TS/solver con la opción --traza, que hace que TS.cpp escriba un JSON con cada
iteración (vecinos evaluados y su estado, vecino elegido, lista tabú). Python solo lo dibuja.
Sin --traza el solver funciona como siempre.

Uso (desde la carpeta vishualaizer/):
    manim -ql --format gif --media_dir visualizaciones/manim animacion_ts.py AnimacionTS

Parámetros opcionales, por variables de entorno:
    TS_INSTANCIA   instancia a usar (por defecto Instance_010.1_new.txt)
    TS_MAX_ITER    máximo de iteraciones a animar (por defecto 1000)
    TS_VELOCIDAD   factor de velocidad; 2 = el doble de rápido (por defecto 1; 0.7 = más lento)
    TS_FILAS_TABU  filas de la lista tabú visibles en pantalla (por defecto 5)
Ejemplo:
    TS_INSTANCIA=Instance_050.1_new.txt TS_MAX_ITER=6 TS_VELOCIDAD=3 manim -ql --format gif animacion_ts.py AnimacionTS

Calidad: -ql (480p), -qm (720p), -qh (1080p).
Para poder pausar y retroceder, generar MP4 en vez de GIF (quitar --format gif); un GIF no se puede pausar.
"""

import os
import sys
import warnings

warnings.filterwarnings("ignore")

import numpy as np
from manim import *  
from manim import Text as _TextBase

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import calcular_coordenadas, ejecutar_solver, leer_instancia, resolver_instancia

ESTADOS = {
    "VALIDO": "válido",
    "NO_EN_F": "descartado: no está en F",
    "SIN_ENERGIA": "descartado: supera la energía E",
    "J_YA_USADO": "descartado: j ya es nodo de otra sortie",
    "NODO_REPETIDO": "descartado: i o k ya usado",
    "TABU": "descartado: movimiento tabú",
}


def ejecutar_ts(ruta_instancia, iteraciones=1000):
    traza = ejecutar_solver(ruta_instancia)

    ruta_ini, mk_ini = traza["ruta_inicial"], traza["mk_inicial"]
    historial = traza["historial"][:iteraciones]
    mejor = (ruta_ini, [], mk_ini)
    mejor_iter = 0
    for reg in historial:
        reg["vuelos"] = [tuple(v) for v in reg["vuelos"]]
        reg["tabu"] = [tuple(t) for t in reg.get("tabu", [])]
        reg["elegido"] = None if reg["elegido"] < 0 else reg["elegido"]
        if reg["elegido"] is not None and reg["es_mejor"]:
            c = reg["candidatos"][reg["elegido"]]
            mejor = (reg["ruta_nueva"], reg["vuelos"] + [(c["i"], c["j"], c["k"])], reg["mk_nuevo"])
            mejor_iter = reg["it"] + 1
    return historial, mejor[0], mejor[1], mejor[2], mejor_iter, ruta_ini, mk_ini


C_DEPOSITO = "#D90429"
C_DRON_APTO = "#06D6A0"
C_SOLO_CAMION = "#8D99AE"
C_ATENDIDO_DRON = "#B15EFF"
C_RUTA_CAMION = "#4DA3FF"
C_RUTA_DRON = "#FF4D6D"
C_VECINO = "#FFD60A"
C_BUENO = "#52E08A"
C_MALO = "#FF6B6B"

MAPA_CENTRO = np.array([-2.7, -0.55, 0.0])
MAPA_ANCHO, MAPA_ALTO = 7.8, 4.7
FUENTE = "Helvetica"
PANEL_X = 2.55
PANEL_ANCHO = 4.5


class Text(_TextBase):
    def __init__(self, texto, **kw):
        kw.setdefault("font", FUENTE)
        super().__init__(texto, **kw)


def fmt_signo(x):
    return ("+" if x > 0 else "−") + f"{abs(x):.2f}"


class AnimacionTS(Scene):
    def construct(self):
        nombre = os.environ.get("TS_INSTANCIA", "Instance_010.1_new.txt")
        max_iter = int(os.environ.get("TS_MAX_ITER", "1000"))
        self.vel = max(float(os.environ.get("TS_VELOCIDAD", "1")), 0.1)
        self.filas_tabu = int(os.environ.get("TS_FILAS_TABU", "5"))

        ruta_inst = resolver_instancia(nombre)
        d = leer_instancia(ruta_inst)
        (historial, mejor_ruta, mejor_vuelos, mejor_mk, mejor_iter,
         ruta_ini, mk_ini) = ejecutar_ts(ruta_inst, max_iter)
        self.d = d

        coords = calcular_coordenadas(d)
        centro = (coords.max(axis=0) + coords.min(axis=0)) / 2
        ext = np.maximum(coords.max(axis=0) - coords.min(axis=0), 1e-9)
        escala = min(MAPA_ANCHO / ext[0], MAPA_ALTO / ext[1])
        self.pos = {i: MAPA_CENTRO + np.array([(coords[i][0] - centro[0]) * escala,
                                               (coords[i][1] - centro[1]) * escala, 0.0])
                    for i in range(d["n"])}
        c = d["c"]
        self.r = float(max(0.06, min(0.25, 1.6 / (c ** 0.5 + 3))))

        self.arrows = {}
        self.dron_lines = {}
        self.nodos = {}
        self.etiquetas = {}
        self.textos = {}
        self.tabu_filas = []
        self.tabu_encabezado = None

        titulo = Text("Tabú Search: camión + dron", font_size=34, weight=BOLD).move_to([-2.85, 3.7, 0])
        sub = Text(d["nombre_archivo"], font_size=20, color=GRAY_B).next_to(titulo, DOWN, buff=0.08)
        self.play(FadeIn(titulo), FadeIn(sub), run_time=self.t(0.8))

        self.caption("1. Los nodos: ¿quién puede ser atendido por dron?")
        self.crear_nodos()
        self.play(LaggedStart(*[FadeIn(self.nodos[i]) for i in self.nodos], lag_ratio=0.06),
                  *[FadeIn(e) for e in self.etiquetas.values()], run_time=self.t(2.0))
        leyenda = self.crear_leyenda()
        self.play(FadeIn(leyenda), run_time=self.t(0.6))
        self.set_panel("info_inst", f"{c} clientes  |  aptos para dron: {len(d['clientes_dron'])}", 3.1, size=20)
        self.set_panel("info_par", f"SL={d['SL']:.0f}s   SR={d['SR']:.0f}s   Energía E={d['E']:.0f}s", 2.65, size=18, color=GRAY_B)
        self.wait(self.t(1.4))

        self.caption("2. Solución inicial del camión (vecino más cercano)")
        flechas = [self.flecha(u, v) for u, v in zip(ruta_ini, ruta_ini[1:])]
        for (u, v), f in zip(zip(ruta_ini, ruta_ini[1:]), flechas):
            self.arrows[(u, v)] = f
        self.play(LaggedStart(*[Create(f) for f in flechas], lag_ratio=0.5), run_time=self.t(0.4 * len(flechas) + 0.5))
        self.set_panel("mk_titulo", "Makespan actual", 1.85, size=18, color=GRAY_B)
        self.set_panel("mk_valor", f"{mk_ini:.2f}", 1.4, size=34, weight=BOLD)
        self.set_panel("mejor", f"Mejor global: {mk_ini:.2f}", 0.85, size=18, color=GRAY_B)
        self.wait(self.t(1.5))

        self.tabu_encabezado = Text("Lista tabú", font_size=20, weight=BOLD).move_to([PANEL_X, -1.75, 0], aligned_edge=LEFT)
        vacio = Text("(vacía)", font_size=17, color=GRAY_B).move_to([PANEL_X, -2.15, 0], aligned_edge=LEFT)
        self.tabu_vacio = vacio
        self.play(FadeIn(self.tabu_encabezado), FadeIn(vacio), run_time=self.t(0.5))

        total = len(historial)
        for reg in historial:
            self.iteracion(reg, total)

        ultimo = historial[-1]
        self.limpiar_panel_vecino()
        if mejor_iter != len(historial) - (0 if ultimo["elegido"] is not None else 1):
            self.caption(f"Fin: se devuelve la mejor solución (iteración {mejor_iter}), no la última")
            self.volver_a_mejor(mejor_ruta, mejor_vuelos)
        else:
            self.caption("Fin: no quedan vecinos válidos. Esta es la mejor solución")
        self.set_panel("mk_valor", f"{mejor_mk:.2f}", 1.4, size=34, weight=BOLD, color=C_BUENO)
        self.set_panel("mejor", f"Mejor global: {mejor_mk:.2f}", 0.85, size=18, color=C_BUENO)
        mejora = mk_ini - mejor_mk
        pct = 100 * mejora / mk_ini if mk_ini else 0
        resumen = VGroup(
            Text("Resultado", font_size=24, weight=BOLD),
            Text(f"Inicial:  {mk_ini:.2f}", font_size=20),
            Text(f"Final:    {mejor_mk:.2f}", font_size=20),
            Text(f"Mejora:  −{mejora:.2f}  ({pct:.2f} %)", font_size=20, color=C_BUENO),
            Text(f"Vuelos de dron: {len(mejor_vuelos)}", font_size=20),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.14).move_to([PANEL_X, -0.35, 0], aligned_edge=LEFT)
        self.play(FadeIn(resumen), run_time=self.t(0.8))
        self.wait(self.t(3))

    def t(self, s):
        return max(s / self.vel, 1 / 15)

    def caption(self, texto):
        nuevo = Text(texto, font_size=22, color=YELLOW_B).move_to([-2.85, 2.85, 0])
        if nuevo.width > 9.0:
            nuevo.scale_to_fit_width(9.0)
        viejo = self.textos.pop("_caption", None)
        if viejo is not None:
            self.remove(viejo)
        self.add(nuevo)
        self.textos["_caption"] = nuevo

    def set_panel(self, clave, texto, y, size=20, color=WHITE, weight=NORMAL, animar=False):
        t = Text(texto, font_size=size, color=color, weight=weight).move_to([PANEL_X, y, 0], aligned_edge=LEFT)
        if t.width > PANEL_ANCHO:
            t.scale_to_fit_width(PANEL_ANCHO)
        viejo = self.textos.pop(clave, None)
        if viejo is not None:
            self.remove(viejo)
        if animar:
            self.play(FadeIn(t), run_time=self.t(0.4))
        else:
            self.add(t)
        self.textos[clave] = t
        return t

    def limpiar_panel_vecino(self):
        for k in ("v1", "v2", "v3", "banner"):
            viejo = self.textos.pop(k, None)
            if viejo is not None:
                self.remove(viejo)

    def crear_nodos(self):
        d, r = self.d, self.r
        for i in range(1, d["c"] + 1):
            color = C_DRON_APTO if i in d["clientes_dron"] else C_SOLO_CAMION
            dot = Dot(self.pos[i], radius=r, color=color, z_index=5)
            dot.set_stroke(WHITE, width=1.5)
            self.nodos[i] = dot
        dep = Square(side_length=2.6 * r, color=C_DEPOSITO, fill_opacity=1, z_index=5).move_to(self.pos[0])
        dep.set_stroke(WHITE, width=2)
        self.nodos[0] = dep
        if r >= 0.12:
            for i in range(1, d["c"] + 1):
                self.etiquetas[i] = Text(str(i), font_size=int(80 * r), color=BLACK, weight=BOLD).move_to(self.pos[i]).set_z_index(6)
            self.etiquetas[0] = Text("0", font_size=int(70 * r), color=WHITE, weight=BOLD).move_to(self.pos[0]).set_z_index(6)

    def color_base(self, i):
        return C_DRON_APTO if i in self.d["clientes_dron"] else C_SOLO_CAMION

    def crear_leyenda(self):
        items = [(C_DEPOSITO, "depósito", "sq"), (C_DRON_APTO, "apto dron", "dot"), (C_SOLO_CAMION, "solo camión", "dot"),
                 (C_ATENDIDO_DRON, "atendido por dron", "dot"), (C_RUTA_CAMION, "ruta camión", "line"),
                 (C_RUTA_DRON, "vuelo dron", "dash")]
        grupo = VGroup()
        for color, texto, tipo in items:
            if tipo == "sq":
                icono = Square(0.16, color=color, fill_opacity=1)
            elif tipo == "dot":
                icono = Dot(radius=0.08, color=color)
            elif tipo == "line":
                icono = Line(LEFT * 0.14, RIGHT * 0.14, color=color, stroke_width=4)
            else:
                icono = DashedLine(LEFT * 0.14, RIGHT * 0.14, color=color, stroke_width=4, dash_length=0.05)
            grupo.add(VGroup(icono, Text(texto, font_size=14, color=GRAY_A)).arrange(RIGHT, buff=0.1))
        grupo.arrange(RIGHT, buff=0.3)
        if grupo.width > 9.0:
            grupo.scale_to_fit_width(9.0)
        return grupo.move_to([-2.85, -3.7, 0])

    def flecha(self, u, v, color=C_RUTA_CAMION):
        p, q = self.pos[u], self.pos[v]
        largo = float(np.linalg.norm(q - p))
        tip = min(0.18, max(0.07, 0.35 * largo))
        return Arrow(p, q, buff=self.r * 1.15, color=color, stroke_width=3.2, tip_length=tip,
                     max_tip_length_to_length_ratio=0.5, z_index=1)

    def lineas_vuelo(self, i, j, k, color, ancho=3.2):
        a = DashedLine(self.pos[i], self.pos[j], color=color, stroke_width=ancho, dash_length=0.1, z_index=2)
        b = DashedLine(self.pos[j], self.pos[k], color=color, stroke_width=ancho, dash_length=0.1, z_index=2)
        return VGroup(a, b).set_z_index(2)

    def anillos(self, i, j, k, color_j, color_ik):
        r = self.r + 0.07
        anillos = VGroup(
            Circle(radius=r, color=color_j, stroke_width=4, z_index=7).move_to(self.pos[j]),
            Circle(radius=r, color=color_ik, stroke_width=3, z_index=7).move_to(self.pos[i]),
            Circle(radius=r, color=color_ik, stroke_width=3, z_index=7).move_to(self.pos[k]),
        )
        return anillos

    def iteracion(self, reg, total):
        it = reg["it"]
        self.caption(f"3. Iteración {it + 1}: vecinos de la solución actual")
        viejo = self.textos.pop("info_inst", None)
        if viejo is not None:
            self.remove(viejo)
        self.set_panel("iter", f"Iteración {it + 1}", 3.1, size=24, weight=BOLD)
        self.set_panel("info_par", "Sacar un cliente j de la ruta y\ndarle un vuelo (i, j, k)", 2.55, size=16, color=GRAY_B)
        self.limpiar_panel_vecino()
        n_cand = len(reg["candidatos"])
        validos = [c for c in reg["candidatos"] if c["valor"] is not None]

        for idx, cand in enumerate(reg["candidatos"]):
            i, j, k = cand["i"], cand["j"], cand["k"]
            valido = cand["valor"] is not None
            color = C_VECINO if valido else GRAY_C
            tmp = VGroup(self.anillos(i, j, k, color, ORANGE if valido else GRAY_C),
                         self.lineas_vuelo(i, j, k, color, ancho=3.6 if valido else 2.0))
            tmp.set_z_index(7)
            self.add(tmp)
            self.set_panel("v1", f"Vecino {idx + 1}/{n_cand}:  sortie ({i},{j},{k})", 0.2, size=19, color=color)
            if valido:
                delta = cand["valor"] - reg["mk_actual"]
                self.set_panel("v2", f"makespan {cand['valor']:.2f}", -0.25, size=19)
                self.set_panel("v3", f"cambio {fmt_signo(delta)}", -0.65, size=19,
                               color=C_BUENO if delta < 0 else C_MALO)
                self.wait(self.t(0.75))
            else:
                self.set_panel("v2", ESTADOS[cand["estado"]], -0.25, size=16, color=GRAY_B)
                self.set_panel("v3", "", -0.65, size=16)
                self.wait(self.t(0.4))
            self.remove(tmp)

        self.limpiar_panel_vecino()

        if reg["elegido"] is None:
            self.caption("4. No queda ningún vecino válido: la búsqueda termina")
            self.set_panel("v1", "Sin vecinos válidos", 0.2, size=20, color=C_MALO)
            self.set_panel("v2", f"{n_cand} candidatos descartados", -0.25, size=17, color=GRAY_B)
            self.wait(self.t(2.0))
            return

        ch = reg["candidatos"][reg["elegido"]]
        i, j, k = ch["i"], ch["j"], ch["k"]
        delta = reg["mk_nuevo"] - reg["mk_actual"]
        self.caption(f"Iteración {it + 1}: se elige el mejor vecino, sortie ({i},{j},{k})")
        oro = VGroup(self.anillos(i, j, k, GOLD, GOLD), self.lineas_vuelo(i, j, k, GOLD, ancho=5))
        oro.set_z_index(7)
        self.play(Create(oro), run_time=self.t(0.7))
        self.set_panel("v1", f"Mejor vecino: sortie ({i},{j},{k})", 0.2, size=19, color=GOLD)
        self.set_panel("v2", f"entre {len(validos)} vecinos válidos", -0.25, size=16, color=GRAY_B)
        self.wait(self.t(1.0))

        self.caption(f"Iteración {it + 1}: el cliente {j} pasa al dron; el camión va de {i} a {k}")
        vieja_1, vieja_2 = self.arrows.pop((i, j)), self.arrows.pop((j, k))
        nueva = self.flecha(i, k)
        self.arrows[(i, k)] = nueva
        vuelo = self.lineas_vuelo(i, j, k, C_RUTA_DRON, ancho=3.6)
        self.dron_lines[(i, j, k)] = vuelo
        self.play(FadeOut(oro), FadeOut(vieja_1), FadeOut(vieja_2), run_time=self.t(0.5))
        self.play(Create(vuelo), Create(nueva),
                  self.nodos[j].animate.set_color(C_ATENDIDO_DRON),
                  Flash(self.pos[j], color=C_ATENDIDO_DRON, flash_radius=self.r + 0.2),
                  run_time=self.t(1.0))

        self.caption(f"Iteración {it + 1}: el movimiento ({i},{j},{k}) entra a la lista tabú")
        self.actualizar_tabu(reg, i, j, k)

        self.caption(f"Iteración {it + 1}: efecto en el makespan")
        color = C_BUENO if delta < 0 else C_MALO
        banner = self.set_panel("banner", f"{reg['mk_actual']:.2f} → {reg['mk_nuevo']:.2f}   ({fmt_signo(delta)})",
                                -1.1, size=21, color=color, weight=BOLD, animar=True)
        self.play(Indicate(banner, color=color), run_time=self.t(0.8))
        self.set_panel("mk_valor", f"{reg['mk_nuevo']:.2f}", 1.4, size=34, weight=BOLD, color=color)
        if reg["es_mejor"]:
            self.set_panel("mejor", f"Mejor global: {reg['mk_nuevo']:.2f}  (nueva mejor)", 0.85, size=18, color=C_BUENO)
        else:
            self.set_panel("mejor", f"Mejor global: {reg['mejor_antes']:.2f}  (esta solución empeora)", 0.85, size=16, color=C_MALO)
        self.wait(self.t(1.6))

    def actualizar_tabu(self, reg, i, j, k):
        it = reg["it"]
        activos = [(a, b, g, e) for (a, b, g, e) in reg["tabu"] if e > it + 1]
        visibles = activos[-self.filas_tabu:]
        if getattr(self, "tabu_vacio", None) is not None:
            self.remove(self.tabu_vacio)
            self.tabu_vacio = None
        nuevas = []
        for n_fila, (a, b, g, e) in enumerate(visibles):
            fila = Text(f"({a},{b},{g})  hasta iteración {e}", font_size=17,
                        color=GOLD if (a, b, g) == (i, j, k) else WHITE)
            fila.move_to([PANEL_X, -2.15 - 0.33 * n_fila, 0], aligned_edge=LEFT)
            nuevas.append(fila)
        antiguas = self.tabu_filas
        self.tabu_filas = nuevas
        anim_fuera = [FadeOut(f) for f in antiguas]
        self.play(*anim_fuera, *[FadeIn(f) for f in nuevas], run_time=self.t(0.7))
        if nuevas:
            self.play(Indicate(nuevas[-1], color=GOLD), run_time=self.t(0.6))
        self.wait(self.t(0.5))

    def volver_a_mejor(self, ruta, vuelos):
        viejas = list(self.arrows.values()) + [g for g in self.dron_lines.values()]
        self.arrows = {}
        self.dron_lines = {}
        nuevas = []
        for u, v in zip(ruta, ruta[1:]):
            f = self.flecha(u, v)
            self.arrows[(u, v)] = f
            nuevas.append(f)
        for (a, b, g) in vuelos:
            lv = self.lineas_vuelo(a, b, g, C_RUTA_DRON, ancho=3.6)
            self.dron_lines[(a, b, g)] = lv
            nuevas.append(lv)
        servidos = {b for (a, b, g) in vuelos}
        recolor = []
        for i in range(1, self.d["c"] + 1):
            color = C_ATENDIDO_DRON if i in servidos else self.color_base(i)
            recolor.append(self.nodos[i].animate.set_color(color))
        self.play(*[FadeOut(m) for m in viejas], *[FadeIn(m) for m in nuevas], *recolor, run_time=self.t(1.5))
        self.wait(self.t(1.0))
