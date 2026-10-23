#include <algorithm>
#include <vector>
#include "makespan.h"

using namespace std;


/*
Función de evaluación. Asume una solución factible; la factibilidad (energía del dron, sorties en F) la valida TS.
*/
double makespan(Solucion & sol, Datos &d){

/*
El makespan es la función de evaluación. Es el clásico de todos los papers de TSP con dron. 
Al final lo que se hace es considerar qué máquina llega primero al depósito ¿camión o dron?
Si llega primero el camión solo, entonces el tiempo total es el del dron a lo que llegue al depósito. -aunque me da la impresión de que las instancias que generaron no consideran posible un sortie ijk con k=0.
Si llega primero el dron solo, entonces el tiempo total es el del camión.
Si llegan juntos el makespan es el del camión.
*/
    int n = d.numero_clientes;
    vector<int> sale(n, -1), llega(n, -1);   // índice de sortie que sale / llega en cada nodo
    for (int s = 0; s < (int)sol.vuelos_dron.size(); s++) {
        sale[sol.vuelos_dron[s].i]  = s;
        llega[sol.vuelos_dron[s].k] = s;
    }

    double t = 0.0, t_lanz = 0.0;
    for (size_t p = 0; p < sol.ruta_camion.size(); p++) {
        int v = sol.ruta_camion[p];
        if (p > 0) t += d.m_traslado_camion[sol.ruta_camion[p-1]][v];

        if (llega[v] != -1) {                 // primero recuperar...
            const Sortie& s = sol.vuelos_dron[llega[v]];
            double t_dron = t_lanz + d.m_traslado_dron[s.i][s.j] + d.m_traslado_dron[s.j][s.k];
            t = max(t, t_dron) + d.SR;
        }
        if (sale[v] != -1) {                  // ...después lanzar (mismo nodo posible)
            t += d.SL;
            t_lanz = t;
        }
    }
    return t;

}
