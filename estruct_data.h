#ifndef ESTRUCT_DATA_H
#define ESTRUCT_DATA_H

#include <vector>
using namespace std;

struct Sortie {int i, j, k;};

struct Solucion {
    vector<int> ruta_camion; // Ruta del camión
    vector<Sortie> vuelos_dron; // Vuelos del dron
};

struct Datos {
    int numero_clientes; // total de nodos de la instancia
    int SL; // tiempo de lanzamiento del dron
    int SR; // tiempo de recuperación del dron
    int F; // número de sorties
    double E; // tiempo máximo de vuelo del dron
    vector<int> clientes_dron; // cantidad de clientes que pueden ser atendidos por un dron
    vector<vector<double>> m_traslado_camion; // Matriz de tiempos de traslado del camión; tamaño numero_clientes x numero_clientes
    vector<vector<double>> m_traslado_dron; // Matriz de tiempos de traslado del dron; tamaño numero_clientes x numero_clientes
    vector<Sortie> sorties; // combinaciones disponibles de vuelos, partiendo en i pasando por j y llegando a k; tamaño |F| x 3
};

#endif
