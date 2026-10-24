"""
Código compartido por visualizador.py (imágenes) y animacion_ts.py (animación):
compilar y ejecutar TS/solver, leer la instancia y reconstruir las posiciones del mapa.
El algoritmo no se implementa aquí: lo ejecuta el C++ y entrega su resultado en un JSON (--traza).
"""

import json
import os
import subprocess
import sys
import tempfile

import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "vishualaizer" else SCRIPT_DIR
TS_DIR = os.path.join(REPO_ROOT, "TS")

ARCHIVOS_CPP = ["main.cpp", "lectura.cpp", "sol_inicial.cpp", "makespan.cpp", "TS.cpp"]
HEADERS = ["estruct_data.h", "lectura.h", "sol_inicial.h", "makespan.h", "TS.h"]


def compilar_solver():
    solver = os.path.join(TS_DIR, "solver")
    fuentes = [os.path.join(TS_DIR, f) for f in ARCHIVOS_CPP + HEADERS]
    if not os.path.exists(solver) or os.path.getmtime(solver) < max(os.path.getmtime(f) for f in fuentes):
        print("[solver] compilando TS/solver ...", file=sys.stderr)
        subprocess.run(["g++", "-std=c++17", "-O2"] + [os.path.join(TS_DIR, f) for f in ARCHIVOS_CPP]
                       + ["-o", solver], check=True)
    return solver


def ejecutar_solver(ruta_instancia):
    solver = compilar_solver()
    with tempfile.TemporaryDirectory() as tmp:
        salida = os.path.join(tmp, "traza.json")
        subprocess.run([solver, ruta_instancia, "--traza", salida], check=True, capture_output=True)
        with open(salida) as f:
            return json.load(f)


def resolver_instancia(ruta):
    for candidata in (ruta,
                      os.path.join(REPO_ROOT, ruta),
                      os.path.join(REPO_ROOT, "instancias", os.path.basename(ruta))):
        if os.path.exists(candidata):
            return os.path.abspath(candidata)
    raise FileNotFoundError(f"No se encontró la instancia: {ruta}")


def leer_instancia(ruta):
    with open(ruta) as f:
        lineas = [l.strip() for l in f if l.strip()]
    c = int(lineas[0])
    SL, SR, E = float(lineas[1]), float(lineas[2]), float(lineas[3])
    clientes_dron = set(map(int, lineas[4].split()))
    n = c + 2
    m_camion = np.array([[float(x) for x in lineas[5 + r].split()] for r in range(n)])
    return dict(c=c, n=n, SL=SL, SR=SR, E=E, clientes_dron=clientes_dron,
                m_camion=m_camion, nombre_archivo=os.path.basename(ruta))


def calcular_coordenadas(d):
    n = d["n"]
    n_pts = n - 1
    D = (d["m_camion"][:n_pts, :n_pts] + d["m_camion"][:n_pts, :n_pts].T) / 2.0
    H = np.eye(n_pts) - np.ones((n_pts, n_pts)) / n_pts
    B = -0.5 * H @ (D ** 2) @ H
    vals, vecs = np.linalg.eigh(B)
    orden = np.argsort(vals)[::-1]
    vals, vecs = vals[orden], vecs[:, orden]
    x = vecs[:, 0] * np.sqrt(max(vals[0], 0.0))
    y = vecs[:, 1] * np.sqrt(max(vals[1], 0.0))
    coords = np.column_stack((x, y))
    return np.vstack([coords, coords[0:1]])
