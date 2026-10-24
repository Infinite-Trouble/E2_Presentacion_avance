#include <limits>
#include <unordered_map>
#include <vector>
#include "TS.h"
#include "makespan.h"
using namespace std;

const int DURACION_TABU = 10; // iteraciones que un movimiento permanece en la lista tabú

/*
Tabú search con un único movimiento: introducir una sortie.
Se saca un cliente j de la ruta del camión y se asigna a un vuelo del dron (i, j, k),
donde i y k son sus vecinos en la ruta actual del camión.
*/
Solucion TS(Solucion inicial, Datos &d, int iteraciones){
    int n = d.numero_clientes;

    // pertenencia a F en O(1): F llega a millones de tripletas en las instancias grandes
    vector<char> en_F((size_t)n * n * n, 0);
    for (const Sortie& s : d.sorties) {
        en_F[((size_t)s.i * n + s.j) * n + s.k] = 1;
    }

    Solucion actual = inicial;
    Solucion mejor = inicial;
    double mejor_makespan = makespan(mejor, d);

    // lista tabú: movimiento (i,j,k) -> iteración hasta la cual está prohibido
    unordered_map<long long, int> tabu;

    for (int it = 0; it < iteraciones; it++) {
        // nodos que ya son lanzamiento / recuperación de alguna sortie
        vector<bool> es_lanzamiento(n, false), es_recuperacion(n, false);
        for (const Sortie& s : actual.vuelos_dron) {
            es_lanzamiento[s.i] = true;
            es_recuperacion[s.k] = true;
        }

        bool hay_vecino = false;
        Solucion mejor_vecino;
        double mejor_vecino_makespan = numeric_limits<double>::infinity();
        long long mejor_vecino_clave = -1;

        // 1. generar vecindario: cada cliente de la ruta es candidato a j de una sortie
        for (size_t p = 1; p + 1 < actual.ruta_camion.size(); p++) {
            int i = actual.ruta_camion[p - 1];
            int j = actual.ruta_camion[p];
            int k = actual.ruta_camion[p + 1];

            // 2. factibilidad
            if (j < 1 || j > n - 2) continue;                                 // a. j es un cliente
            if (!en_F[((size_t)i * n + j) * n + k]) continue;                 // b. la sortie está en F
            if (d.m_traslado_dron[i][j] + d.m_traslado_dron[j][k] > d.E) continue; // c. energía del dron
            if (es_lanzamiento[j] || es_recuperacion[j]) continue;            // j no puede ser nodo de otra sortie
            if (es_lanzamiento[i] || es_recuperacion[k]) continue;            // un lanzamiento / recuperación por nodo

            Solucion vecino = actual;
            vecino.ruta_camion.erase(vecino.ruta_camion.begin() + p);
            vecino.vuelos_dron.push_back({i, j, k});
            double valor = makespan(vecino, d);

            // 3. mejor vecino fuera de la lista tabú (o tabú que mejora la mejor solución: aspiración)
            long long clave = ((long long)i * n + j) * n + k;
            auto t = tabu.find(clave);
            bool es_tabu = (t != tabu.end() && t->second > it);
            if (es_tabu && valor >= mejor_makespan) continue;

            if (valor < mejor_vecino_makespan) {
                hay_vecino = true;
                mejor_vecino = vecino;
                mejor_vecino_makespan = valor;
                mejor_vecino_clave = clave;
            }
        }

        // criterio de parada: no quedan movimientos posibles
        if (!hay_vecino) break;

        // 4. mover y declarar el movimiento tabú
        actual = mejor_vecino;
        tabu[mejor_vecino_clave] = it + DURACION_TABU;

        // 5. actualizar mejor solución
        if (mejor_vecino_makespan < mejor_makespan) {
            mejor = actual;
            mejor_makespan = mejor_vecino_makespan;
        }
    }

    return mejor;
}
