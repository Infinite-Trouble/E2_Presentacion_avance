
"""
Visualizador para el Problema del Vendedor Viajero con Camión y Dron (TSP-D / FSTSP)
Resuelto mediante Tabu Search (TS).

Genera:
1. Mapa inicial de nodos y depósito.
2. Mapa de la solución inicial (solo camión) con makespan.
3. Mapa de la solución final (camión + vuelos de dron) con makespan.
4. Panel comparativo de las 3 etapas lado a lado.
"""

import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import matplotlib.lines as mlines

from comun import SCRIPT_DIR, calcular_coordenadas, ejecutar_solver, leer_instancia, resolver_instancia

DEFAULT_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "visualizaciones")


# ==========================================
# 1. RESULTADO DEL SOLVER C++
# ==========================================
def resultado_solver(ruta_instancia):
    traza = ejecutar_solver(ruta_instancia)
    return {
        "makespan_inicial": traza["mk_inicial"],
        "ruta_inicial": traza["ruta_inicial"],
        "makespan_final": traza["mk_final"],
        "ruta_final": traza["ruta_final"],
        "sorties": [tuple(v) for v in traza["vuelos_final"]],
    }


# ==========================================
# 2. FUNCIONES DE DIBUJO Y VISUALIZACIÓN
# ==========================================
# Paleta de colores moderna y clara
COLOR_DEPOT = "#D90429"       # Rojo carmesí para el depósito
COLOR_DRONE_CLI = "#06D6A0"   # Verde esmeralda para clientes aptos para dron
COLOR_TRUCK_CLI = "#6C757D"   # Gris pizarra para clientes solo camión
COLOR_TRUCK_ROUTE = "#1D3557" # Azul marino profundo para la ruta del camión
COLOR_DRONE_ROUTE = "#E63946" # Rojo brillante / magenta para el dron
COLOR_DRONE_SERVED = "#9D4EDD" # Púrpura para cliente atendido por dron


def configurar_estilo_ejes(ax, coords, titulo, info_texto=None):
    """Aplica formato visual consistente a los gráficos."""
    ax.set_title(titulo, fontsize=13, fontweight="bold", pad=12, color="#212529")
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, linestyle="--", alpha=0.3, color="#adb5bd")
    ax.set_facecolor("#f8f9fa")

    # Margen proporcional
    margin_x = (coords[:, 0].max() - coords[:, 0].min()) * 0.12 or 1.0
    margin_y = (coords[:, 1].max() - coords[:, 1].min()) * 0.12 or 1.0
    ax.set_xlim(coords[:, 0].min() - margin_x, coords[:, 0].max() + margin_x)
    ax.set_ylim(coords[:, 1].min() - margin_y, coords[:, 1].max() + margin_y)

    ax.set_xlabel("Coordenada X (reconstruida)", fontsize=9, color="#495057")
    ax.set_ylabel("Coordenada Y (reconstruida)", fontsize=9, color="#495057")
    ax.tick_params(labelsize=8, colors="#6c757d")

    if info_texto:
        props = dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="#ced4da", alpha=0.92)
        ax.text(0.02, 0.98, info_texto, transform=ax.transAxes, fontsize=9,
                verticalalignment="top", bbox=props, family="monospace")


def dibujar_nodos_base(ax, datos, coords, resaltar_sorties=None):
    """
    Dibuja los nodos en el mapa:
    - Depósito (nodo 0 / n-1)
    - Clientes elegibles para dron
    - Clientes solo camión
    - (Opcional) Resalta nodos de lanzamiento, atención por dron y recuperación
    """
    c = datos["c"]
    clientes_dron = datos["clientes_dron"]

    sorties_info = {}
    if resaltar_sorties:
        for i, j, k in resaltar_sorties:
            sorties_info[j] = "atendido_dron"
            sorties_info[i] = "lanzamiento"
            sorties_info[k] = "recuperacion"

    # Dibujar clientes (1 a c)
    for nodo in range(1, c + 1):
        x, y = coords[nodo]
        es_dron = nodo in clientes_dron
        rol_sortie = sorties_info.get(nodo, None)

        if rol_sortie == "atendido_dron":
            color = COLOR_DRONE_SERVED
            borde = "#3c096c"
            marcador = "o"
            tamano = 160
        elif es_dron:
            color = COLOR_DRONE_CLI
            borde = "#0f5132"
            marcador = "o"
            tamano = 120
        else:
            color = COLOR_TRUCK_CLI
            borde = "#343a40"
            marcador = "o"
            tamano = 110

        ax.scatter(x, y, s=tamano, c=color, edgecolors=borde, linewidths=1.8, zorder=5)

        # Etiqueta numérica
        ax.annotate(str(nodo), (x, y), color="white", weight="bold",
                    fontsize=8, ha="center", va="center", zorder=6)

    # Dibujar depósito (nodo 0)
    x0, y0 = coords[0]
    ax.scatter(x0, y0, s=280, c=COLOR_DEPOT, marker="s", edgecolors="#67000d", linewidths=2.2, zorder=7)
    ax.annotate("0 (Depósito)", (x0, y0), xytext=(0, -18), textcoords="offset points",
                color="#800000", weight="bold", fontsize=9, ha="center", va="top",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="#ffe3e3", edgecolor="#ff8787", alpha=0.9),
                zorder=8)


def dibujar_flecha_ruta(ax, p1, p2, color=COLOR_TRUCK_ROUTE, estilo="-", grosor=1.8, curvatura=0.0):
    """Dibuja una arista dirigida con flecha entre dos puntos."""
    patch = FancyArrowPatch(
        posA=p1, posB=p2,
        connectionstyle=f"arc3,rad={curvatura}",
        color=color,
        arrowstyle="-|>,head_length=5,head_width=3",
        linestyle=estilo,
        linewidth=grosor,
        shrinkA=9, shrinkB=9,
        zorder=3
    )
    ax.add_patch(patch)


# ==========================================
# 3. GENERADORES DE LOS 3 MAPAS
# ==========================================
def generar_mapa_1_inicial(datos, coords, ax=None):
    """1. Mapa inicial donde se posicionan todos los nodos a visitar."""
    crear_figura = ax is None
    if crear_figura:
        fig, ax = plt.subplots(figsize=(8, 7), dpi=150)

    dibujar_nodos_base(ax, datos, coords)

    info = (
        f"--- DATOS DE INSTANCIA ---\n"
        f"Archivo: {datos['nombre_archivo']}\n"
        f"Total clientes: {datos['c']}\n"
        f"Aptos para dron: {len(datos['clientes_dron'])}\n"
        f"Solo camión: {datos['c'] - len(datos['clientes_dron'])}\n"
        f"T. Lanzamiento (SL): {datos['SL']} s\n"
        f"T. Recuperación (SR): {datos['SR']} s\n"
        f"Autonomía dron (E): {datos['E']} s"
    )

    titulo = f"1. Mapa Inicial: Ubicación de Nodos y Depósito\n({datos['nombre_archivo']})"
    configurar_estilo_ejes(ax, coords, titulo, info)

    # Leyenda
    leyenda_elementos = [
        mlines.Line2D([], [], color=COLOR_DEPOT, marker='s', linestyle='None',
                      markersize=10, label='Depósito (Salida / Regreso)'),
        mlines.Line2D([], [], color=COLOR_DRONE_CLI, marker='o', linestyle='None',
                      markersize=8, label=f'Cliente apto para dron ({len(datos["clientes_dron"])})'),
        mlines.Line2D([], [], color=COLOR_TRUCK_CLI, marker='o', linestyle='None',
                      markersize=8, label=f'Cliente solo camión ({datos["c"] - len(datos["clientes_dron"])})'),
    ]
    ax.legend(handles=leyenda_elementos, loc="upper right", fontsize=8, framealpha=0.9)

    if crear_figura:
        fig.tight_layout()
        return fig
    return None


def generar_mapa_2_solucion_inicial(datos, coords, ruta_inicial, makespan_ini, ax=None):
    """2. Mapa de la solución inicial que contempla solo una ruta de camión."""
    crear_figura = ax is None
    if crear_figura:
        fig, ax = plt.subplots(figsize=(8, 7), dpi=150)

    dibujar_nodos_base(ax, datos, coords)

    # Dibujar ruta del camión
    for idx in range(len(ruta_inicial) - 1):
        u = ruta_inicial[idx]
        v = ruta_inicial[idx + 1]
        p1 = coords[u]
        p2 = coords[v]
        dibujar_flecha_ruta(ax, p1, p2, color=COLOR_TRUCK_ROUTE, estilo="-", grosor=2.0)

    secuencia_str = " -> ".join(map(str, ruta_inicial[:8]))
    if len(ruta_inicial) > 8:
        secuencia_str += " -> ..."

    info = (
        f"--- SOLUCIÓN INICIAL (NN) ---\n"
        f"Makespan inicial: {makespan_ini:.2f} s\n"
        f"Clientes atendidos camión: {datos['c']}\n"
        f"Sorties de dron: 0\n"
        f"Ruta: {secuencia_str}"
    )

    titulo = f"2. Solución Inicial: Solo Ruta de Camión\nMakespan: {makespan_ini:.2f} s"
    configurar_estilo_ejes(ax, coords, titulo, info)

    leyenda_elementos = [
        mlines.Line2D([], [], color=COLOR_DEPOT, marker='s', linestyle='None',
                      markersize=9, label='Depósito'),
        mlines.Line2D([], [], color=COLOR_DRONE_CLI, marker='o', linestyle='None',
                      markersize=8, label='Cliente'),
        mlines.Line2D([], [], color=COLOR_TRUCK_ROUTE, lw=2.2,
                      label=f'Ruta del Camión (Makespan: {makespan_ini:.2f} s)'),
    ]
    ax.legend(handles=leyenda_elementos, loc="upper right", fontsize=8, framealpha=0.9)

    if crear_figura:
        fig.tight_layout()
        return fig
    return None


def generar_mapa_3_solucion_final(datos, coords, ruta_final, sorties, makespan_fin, makespan_ini=None, ax=None):
    """3. Mapa de la solución final con la ruta del camión y del dron."""
    crear_figura = ax is None
    if crear_figura:
        fig, ax = plt.subplots(figsize=(8, 7), dpi=150)

    # Resaltar clientes según su atención
    dibujar_nodos_base(ax, datos, coords, resaltar_sorties=sorties)

    # 1. Dibujar ruta del camión
    for idx in range(len(ruta_final) - 1):
        u = ruta_final[idx]
        v = ruta_final[idx + 1]
        p1 = coords[u]
        p2 = coords[v]
        dibujar_flecha_ruta(ax, p1, p2, color=COLOR_TRUCK_ROUTE, estilo="-", grosor=2.2)

    # 2. Dibujar vuelos del dron (sorties: i -> j -> k)
    for num_s, (i, j, k) in enumerate(sorties, start=1):
        p_i = coords[i]
        p_j = coords[j]
        p_k = coords[k]

        # Vuelo de ida: Lanzamiento i -> Cliente j
        dibujar_flecha_ruta(ax, p_i, p_j, color=COLOR_DRONE_ROUTE, estilo="--", grosor=1.8, curvatura=0.15)
        # Vuelo de regreso: Cliente j -> Recuperación k
        dibujar_flecha_ruta(ax, p_j, p_k, color=COLOR_DRONE_ROUTE, estilo="--", grosor=1.8, curvatura=0.15)

    # Texto de mejora
    mejora_texto = ""
    if makespan_ini is not None and makespan_ini > 0:
        delta = makespan_ini - makespan_fin
        pct = (delta / makespan_ini) * 100.0
        mejora_texto = f"Mejora respecto inicial: -{delta:.2f} s ({pct:.2f}%)\n"

    sorties_resumen = ", ".join([f"({i},{j},{k})" for i, j, k in sorties[:5]])
    if len(sorties) > 5:
        sorties_resumen += f" ... (+{len(sorties)-5} más)"

    info = (
        f"--- SOLUCIÓN FINAL (TS) ---\n"
        f"Makespan final: {makespan_fin:.2f} s\n"
        f"{mejora_texto}"
        f"Sorties realizadas: {len(sorties)}\n"
        f"Clientes vía dron: {len(sorties)}\n"
        f"Sorties: {sorties_resumen}"
    )

    titulo = f"3. Solución Final: Camión + Dron (TS)\nMakespan: {makespan_fin:.2f} s"
    configurar_estilo_ejes(ax, coords, titulo, info)

    leyenda_elementos = [
        mlines.Line2D([], [], color=COLOR_DEPOT, marker='s', linestyle='None',
                      markersize=9, label='Depósito'),
        mlines.Line2D([], [], color=COLOR_TRUCK_ROUTE, lw=2.2,
                      label='Ruta Camión'),
        mlines.Line2D([], [], color=COLOR_DRONE_ROUTE, lw=1.8, linestyle='--',
                      label='Vuelo Dron (i -> j -> k)'),
        mlines.Line2D([], [], color=COLOR_DRONE_SERVED, marker='o', linestyle='None',
                      markersize=8, label='Cliente atendido por dron'),
    ]
    ax.legend(handles=leyenda_elementos, loc="upper right", fontsize=8, framealpha=0.9)

    if crear_figura:
        fig.tight_layout()
        return fig
    return None


def generar_panel_comparativo(datos, coords, ruta_ini, makespan_ini, ruta_fin, sorties, makespan_fin):
    """Genera una imagen con los 3 mapas lado a lado en un panel comparativo."""
    fig, axes = plt.subplots(1, 3, figsize=(22, 7.5), dpi=150)

    generar_mapa_1_inicial(datos, coords, ax=axes[0])
    generar_mapa_2_solucion_inicial(datos, coords, ruta_ini, makespan_ini, ax=axes[1])
    generar_mapa_3_solucion_final(datos, coords, ruta_fin, sorties, makespan_fin, makespan_ini, ax=axes[2])

    delta = makespan_ini - makespan_fin
    pct = (delta / makespan_ini) * 100.0 if makespan_ini > 0 else 0.0

    fig.suptitle(
        f"Optimización TSP-D con Tabu Search | Instancia: {datos['nombre_archivo']}\n"
        f"Makespan Inicial: {makespan_ini:.2f} s  ->  Makespan Final: {makespan_fin:.2f} s  "
        f"(Mejora: {delta:.2f} s / -{pct:.2f}%)",
        fontsize=15, fontweight="bold", y=1.02
    )

    fig.tight_layout()
    return fig


# ==========================================
# 4. FUNCIÓN PRINCIPAL
# ==========================================
def main():
    parser = argparse.ArgumentParser(
        description="Visualizador de TSP con Camión y Dron (Tabu Search)"
    )
    parser.add_argument("instancia", help="Ruta al archivo de instancia (.txt)")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Directorio donde guardar las imágenes (default: vishualaizer/visualizaciones)")
    parser.add_argument("--show", action="store_true", help="Mostrar ventanas interactivas con matplotlib")

    args = parser.parse_args()

    print("=" * 60)
    print("  VISUALIZADOR TSP-D: CAMIÓN Y DRON (TABU SEARCH)")
    print("=" * 60)

    # 1. Leer datos de la instancia
    ruta_inst = resolver_instancia(args.instancia)
    print(f"[*] Leyendo instancia: {ruta_inst}")
    datos = leer_instancia(ruta_inst)
    print(f"    - Clientes: {datos['c']}")
    print(f"    - Clientes aptos para dron: {len(datos['clientes_dron'])}")
    print(f"    - SL={datos['SL']}s, SR={datos['SR']}s, Autonomía={datos['E']}s")

    # 2. Calcular coordenadas 2D por MDS
    print("[*] Reconstruyendo coordenadas 2D (MDS)...")
    coords = calcular_coordenadas(datos)

    # 3. Obtener resultados del solver C++
    print("[*] Ejecutando TS/solver ...")
    resultado = resultado_solver(ruta_inst)

    makespan_ini = resultado["makespan_inicial"]
    ruta_ini = resultado["ruta_inicial"]
    makespan_fin = resultado["makespan_final"]
    ruta_fin = resultado["ruta_final"]
    sorties = resultado["sorties"]

    print("\n--- RESUMEN DE RESULTADOS ---")
    print(f"Makespan Inicial: {makespan_ini:.2f} s")
    print(f"Makespan Final:   {makespan_fin:.2f} s")
    if makespan_ini:
        delta = makespan_ini - makespan_fin
        pct = (delta / makespan_ini) * 100.0
        print(f"Mejora conseguida: {delta:.2f} s ({pct:.2f}%)")
    print(f"Ruta Final Camión: {' -> '.join(map(str, ruta_fin))}")
    print(f"Sorties del Dron:  {len(sorties)} vuelos")
    for s in sorties:
        print(f"   Lanzamiento: {s[0]} -> Cliente Dron: {s[1]} -> Recuperación: {s[2]}")
    print("-----------------------------\n")

    # 4. Crear directorio de salida
    os.makedirs(args.output_dir, exist_ok=True)
    nombre_base = os.path.splitext(datos["nombre_archivo"])[0]

    # 5. Generar y guardar figuras
    print(f"[*] Generando mapas en {args.output_dir}...")

    # Mapa 1: Inicial
    fig1 = generar_mapa_1_inicial(datos, coords)
    path1 = os.path.join(args.output_dir, f"{nombre_base}_1_mapa_inicial.png")
    fig1.savefig(path1, bbox_inches="tight")
    plt.close(fig1)
    print(f"    [+] Guardado: {path1}")

    # Mapa 2: Solución Inicial
    fig2 = generar_mapa_2_solucion_inicial(datos, coords, ruta_ini, makespan_ini)
    path2 = os.path.join(args.output_dir, f"{nombre_base}_2_solucion_inicial.png")
    fig2.savefig(path2, bbox_inches="tight")
    plt.close(fig2)
    print(f"    [+] Guardado: {path2}")

    # Mapa 3: Solución Final
    fig3 = generar_mapa_3_solucion_final(datos, coords, ruta_fin, sorties, makespan_fin, makespan_ini)
    path3 = os.path.join(args.output_dir, f"{nombre_base}_3_solucion_final.png")
    fig3.savefig(path3, bbox_inches="tight")
    plt.close(fig3)
    print(f"    [+] Guardado: {path3}")

    # Panel Comparativo (3 en 1)
    fig_comp = generar_panel_comparativo(datos, coords, ruta_ini, makespan_ini, ruta_fin, sorties, makespan_fin)
    path_comp = os.path.join(args.output_dir, f"{nombre_base}_comparativa.png")
    fig_comp.savefig(path_comp, bbox_inches="tight")
    plt.close(fig_comp)
    print(f"    [+] Guardado: {path_comp}")

    # Si se solicitó mostrar en pantalla
    if args.show:
        print("[*] Abriendo visualización interactiva...")
        fig_show = generar_panel_comparativo(datos, coords, ruta_ini, makespan_ini, ruta_fin, sorties, makespan_fin)
        plt.show()

    print("\n[OK] ¡Visualización completada exitosamente!")


if __name__ == "__main__":
    main()
