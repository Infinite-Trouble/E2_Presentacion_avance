#include <algorithm>
#include <iomanip>
#include <limits>
#include <ostream>
#include <unordered_map>
#include <vector>
#include "TS.h"
#include "makespan.h"
using namespace std;

const int DURACION_TABU = 10; // iteraciones que un movimiento permanece en la lista tabú

// --- escritura de la traza (solo se usa si TS recibe un flujo `traza`) ---
static void escribir_ruta(ostream& o, const vector<int>& ruta) {
    o << "[";
    for (size_t x = 0; x < ruta.size(); x++) o << (x ? "," : "") << ruta[x];
    o << "]";
}

static void escribir_vuelos(ostream& o, const vector<Sortie>& vuelos) {
    o << "[";
    for (size_t x = 0; x < vuelos.size(); x++) {
        o << (x ? "," : "") << "[" << vuelos[x].i << "," << vuelos[x].j << "," << vuelos[x].k << "]";
    }
    o << "]";
}

/*
Tabú search con un único movimiento: introducir una sortie.
Se saca un cliente j de la ruta del camión y se asigna a un vuelo del dron (i, j, k),
donde i y k son sus vecinos en la ruta actual del camión.
*/
Solucion TS(Solucion inicial, Datos &d, int iteraciones, ostream* traza){
    int n = d.numero_clientes;

    // pertenencia a F en O(1)
    vector<char> en_F((size_t)n * n * n, 0);
    for (const Sortie& s : d.sorties) {
        en_F[((size_t)s.i * n + s.j) * n + s.k] = 1;
    }

    Solucion actual = inicial;
    Solucion mejor = inicial;
    double mejor_makespan = makespan(mejor, d);
    int mejor_iter = 0;

    // lista tabú: movimiento (i,j,k) + iteración hasta la cual está prohibido
    unordered_map<long long, int> tabu;


    if (traza) {
        *traza << setprecision(12) << "{\"mk_inicial\":" << mejor_makespan << ",\"ruta_inicial\":";
        escribir_ruta(*traza, inicial.ruta_camion);
        *traza << ",\"historial\":[";
    }

    for (int it = 0; it < iteraciones; it++) {
        // nodos que ya son lanzamiento / recuperación de alguna sortie
        vector<bool> es_lanzamiento(n, false), es_recuperacion(n, false);
        for (const Sortie& s : actual.vuelos_dron) {
            es_lanzamiento[s.i] = true;
            es_recuperacion[s.k] = true;
        }


        if (traza) {
            double mk_actual = makespan(actual, d);
            *traza << (it ? "," : "") << "{\"it\":" << it << ",\"mk_actual\":" << mk_actual
                   << ",\"mejor_antes\":" << mejor_makespan << ",\"ruta\":";
            escribir_ruta(*traza, actual.ruta_camion);
            *traza << ",\"vuelos\":";
            escribir_vuelos(*traza, actual.vuelos_dron);
            *traza << ",\"candidatos\":[";
        }
        int n_candidatos = 0;
        // registra un candidato evaluado y su estado (valor < 0: no se llegó a evaluar)
        auto anotar = [&](const char* estado, int i, int j, int k, int pos, double valor) {
            if (traza) {
                *traza << (n_candidatos ? "," : "") << "{\"pos\":" << pos << ",\"i\":" << i << ",\"j\":" << j
                       << ",\"k\":" << k << ",\"estado\":\"" << estado << "\",\"valor\":";
                if (valor < 0) *traza << "null"; else *traza << valor;
                *traza << "}";
            }
            n_candidatos++;
        };

        bool hay_vecino = false;
        Solucion mejor_vecino;
        double mejor_vecino_makespan = numeric_limits<double>::infinity();
        long long mejor_vecino_clave = -1;
        int mejor_vecino_idx = -1;

        // 1. generar vecindario: cada cliente de la ruta es candidato a j de una sortie
        for (size_t p = 1; p + 1 < actual.ruta_camion.size(); p++) {
            int i = actual.ruta_camion[p - 1];
            int j = actual.ruta_camion[p];
            int k = actual.ruta_camion[p + 1];

            // 2. factibilidad
            if (j < 1 || j > n - 2) continue;                                 // a. j es un cliente
            if (!en_F[((size_t)i * n + j) * n + k]) { anotar("NO_EN_F", i, j, k, p, -1); continue; }  // b. la sortie está en F
            if (d.m_traslado_dron[i][j] + d.m_traslado_dron[j][k] > d.E) { anotar("SIN_ENERGIA", i, j, k, p, -1); continue; } // c. energía del dron
            if (es_lanzamiento[j] || es_recuperacion[j]) { anotar("J_YA_USADO", i, j, k, p, -1); continue; }  // j no puede ser nodo de otra sortie
            if (es_lanzamiento[i] || es_recuperacion[k]) { anotar("NODO_REPETIDO", i, j, k, p, -1); continue; } // un lanzamiento / recuperación por nodo

            Solucion vecino = actual;
            vecino.ruta_camion.erase(vecino.ruta_camion.begin() + p);
            vecino.vuelos_dron.push_back({i, j, k});
            double valor = makespan(vecino, d);

            // 3. mejor vecino fuera de la lista tabú
            long long clave = ((long long)i * n + j) * n + k;
            auto t = tabu.find(clave);
            bool es_tabu = (t != tabu.end() && t->second > it);
            if (es_tabu && valor >= mejor_makespan) { anotar("TABU", i, j, k, p, valor); continue; }

            if (valor < mejor_vecino_makespan) {
                hay_vecino = true;
                mejor_vecino = vecino;
                mejor_vecino_makespan = valor;
                mejor_vecino_clave = clave;
                mejor_vecino_idx = n_candidatos;
            }
            anotar("VALIDO", i, j, k, p, valor);
        }

        if (traza) *traza << "],\"elegido\":" << mejor_vecino_idx;

        // criterio de parada: no quedan movimientos posibles
        if (!hay_vecino) {
            if (traza) *traza << "}";
            break;
        }

        // 4. mover y declarar el movimiento tabú
        actual = mejor_vecino;
        tabu[mejor_vecino_clave] = it + DURACION_TABU;

        // 5. actualizar mejor solución
        bool es_mejor = mejor_vecino_makespan < mejor_makespan;
        if (es_mejor) {
            mejor = actual;
            mejor_makespan = mejor_vecino_makespan;
            mejor_iter = it + 1;
        }

        if (traza) {
            // lista tabú todavía activa en la próxima iteración, en orden de inserción
            vector<pair<int, long long>> activos;
            for (const auto& e : tabu) if (e.second > it + 1) activos.push_back({e.second, e.first});
            sort(activos.begin(), activos.end());
            *traza << ",\"mk_nuevo\":" << mejor_vecino_makespan << ",\"es_mejor\":" << (es_mejor ? "true" : "false")
                   << ",\"ruta_nueva\":";
            escribir_ruta(*traza, actual.ruta_camion);
            *traza << ",\"tabu\":[";
            for (size_t x = 0; x < activos.size(); x++) {
                long long c = activos[x].second;
                *traza << (x ? "," : "") << "[" << c / n / n << "," << (c / n) % n << "," << c % n << "," << activos[x].first << "]";
            }
            *traza << "]}";
        }
    }

    if (traza) {
        *traza << "],\"mejor_iter\":" << mejor_iter << ",\"mk_final\":" << mejor_makespan << ",\"ruta_final\":";
        escribir_ruta(*traza, mejor.ruta_camion);
        *traza << ",\"vuelos_final\":";
        escribir_vuelos(*traza, mejor.vuelos_dron);
        *traza << "}\n";
    }

    return mejor;
}
