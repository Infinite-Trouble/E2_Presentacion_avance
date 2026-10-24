#include <vector>
#include <limits>
#include "sol_inicial.h"
using namespace std;
/*
Solución inicial con vecino más cercano.
*/
Solucion NN(Datos &datos){
    /*
    Siguiendo la lógica planteada por Boysen, se partirá con una solución que utiliza solo una ruta de camión.
    Se seguirá la heurística del vecino más cercano para construir la ruta del camión, puesto que es de bajo costo.
    Las rutas del dron parten vacías.
    El makespan de esta solución inicial es la ruta del camión, la cual será la peor solución posible en todo caso.
    */

    int n = datos.numero_clientes;

    Solucion solucion;

    vector<bool> visitado(n, false);


    // partimos en el depósito, que es el nodo 0
    int actual = 0;
    visitado[actual] = true;
    solucion.ruta_camion.push_back(actual);

    // Ahora visitamos a todo el resto de los clientes:

    for(int i = 0; i< n;i++){
        int mejor_vecino = -1;
        double mejorTiempo = numeric_limits<double>::infinity(); 

        for(int j = 0; j<n-1; j++){ // n-1 es el depósito final, no un cliente
            if(!visitado[j] && datos.m_traslado_camion[actual][j] < mejorTiempo){
                mejorTiempo = datos.m_traslado_camion[actual][j];
                mejor_vecino = j;
            }
        }

        if(mejor_vecino == -1) break;

        solucion.ruta_camion.push_back(mejor_vecino);
        visitado[mejor_vecino] = true;
        actual = mejor_vecino;

    }
    // agregamos la vuelta al depósito (nodo n-1)
    solucion.ruta_camion.push_back(n-1);


    return solucion;

}
