#include <iostream>
#include <fstream>
#include <string>
#include <limits>
#include <vector>
#include "lectura.h"

using namespace std;


/*

Representación de solución: check
Movimientos:
Manejo de restricciones:
Tabu search?: 

            material de referencia:
            https://github.com/Xavier-MaYiMing/Tabu-Search/blob/main/TS.py



Función de evaluación: check




*/

struct Solucion {
    vector<int> ruta_camion; // Ruta del camión
    vector<Sortie> vuelos_dron; // Vuelos del dron
    double tiempo_total; // Tiempo total de la solución
};



/*
El makespan es la función de evaluación. Es el clásico de todos los papers de TSP con dron. 
Al final lo que se hace es considerar qué máquina llega primero al depósito ¿camión o dron?
Si llega primero el camión solo, entonces el tiempo total es el del dron a lo que llegue al depósito. -aunque me da la impresión de que las instancias que generaron no consideran posible un sortie ijk con k=0.
Si llega primero el dron solo, entonces el tiempo total es el del camión.
Si llegan juntos el makespan es el del camión.
*/
double makespan(Solucion & sol, Datos &d){
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



Solucion NN(Datos &datos){
    /*
    Siguiendo la lógica planteada por Boysen, se partirá con una solución que utiliza solo una ruta de camión.
    Se seguirá la heurística del vecino más cercano para construir la ruta del camión, puesto que es de bajo costo.
    Las rutas del dron parten vacías.
    El makespan de esta solución inicial es la ruta del camión, la cual será la peor solución posible en todo caso.
    */

    int n = datos.numero_clientes;

    Solucion solucion;
    solucion.tiempo_total = 0.0;

    vector<bool> visitado(n, false);


    // partimos en el depósito, que es el nodo 0
    int actual = 0;
    visitado[actual] = true;
    solucion.ruta_camion.push_back(actual);

    // Ahora visitamos a todo el resto de los clientes:

    for(int i = 0; i< n;i++){
        int mejor_vecino = -1;
        double mejorTiempo = numeric_limits<double>::infinity(); 

        for(int j = 0; j<n; j++){
            if(!visitado[j] && datos.m_traslado_camion[actual][j] < mejorTiempo){
                mejorTiempo = datos.m_traslado_camion[actual][j];
                mejor_vecino = j;
            }
        }

        if(mejor_vecino == -1) break;

        solucion.ruta_camion.push_back(mejor_vecino);
        visitado[mejor_vecino] = true;
        actual = mejor_vecino;
        solucion.tiempo_total += mejorTiempo;

    }
    // agregamos la vuelta al depósito
    solucion.ruta_camion.push_back(0);
    solucion.tiempo_total += datos.m_traslado_camion[actual][0];


    return solucion;

};

int main() {

    // Leemos la instancia:

    // Damos la solución inicial
    
    return 0;
}