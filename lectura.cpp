#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <limits>
using namespace std;

struct Sortie {int i, j, k;};

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

Datos leer_datos(istream& archivo){
    Datos datos;
    archivo >> datos.numero_clientes >> datos.SL >> datos.SR >> datos.E;
    datos.numero_clientes += 2; // considerando que hay una salida y llegada al depósito

    // Eliminamos el salto de línea. No hay instancia que no tenga lista de clientes de dron, así que todo bien con esto.
    archivo >> ws; // https://cplusplus.com/reference/istream/ws/ así se ve fino

    // Leer la lista de clientes que pueden ser atendidos por el dron
    string linea_clientes_dron;
    getline(archivo, linea_clientes_dron);
    istringstream iss(linea_clientes_dron);
    int cliente;
    while (iss >> cliente) {
        datos.clientes_dron.push_back(cliente);
    }

    // Leer la matriz de traslado del camión y del dron
    int n = datos.numero_clientes;
    datos.m_traslado_camion.resize(n, vector<double>(n));
    datos.m_traslado_dron.resize(n, vector<double>(n));
    for (auto& fila : datos.m_traslado_camion) {
        for (auto& nodo : fila){
            archivo >> nodo;
            }
        }
    for (auto& fila : datos.m_traslado_dron) {
        for (auto& nodo : fila){
            archivo >> nodo;
            }
        }

    // Leemos F, que determina el número de sorties.
    archivo >> datos.F;


    // Leer las sorties
    datos.sorties.resize(datos.F);
    for (auto& sortie: datos.sorties) {
        archivo >> sortie.i >> sortie.j >> sortie.k;
    }
    return datos;
}



int main(int argc, char* argv[]) {
    if (argc < 2) {
        cerr << "Uso: " << argv[0] << " <archivo_de_datos>" << endl;
        return 1;
    }

    ifstream archivo(argv[1]);
    if (!archivo) {
        cerr << "No se pudo abrir el archivo: " << argv[1] << endl;
        return 1;
    }

    Datos datos = leer_datos(archivo);

    // En rigor el programa para hacer los experimentos corre hasta acá.
    // Ya cumplió su función de leer la instancia y guardarle en memoria.
    // Lo imprimí para confirmar que salían bien los datos.



    cout << "Número de clientes: " << datos.numero_clientes -2 << endl;
    cout << "Tiempo de lanzamiento del dron (SL): " << datos.SL << endl;
    cout << "Tiempo de recuperación del dron (SR): " << datos.SR << endl;
    cout << "Tiempo máximo de vuelo del dron (E): " << datos.E << endl;

    cout << "Clientes que pueden ser atendidos por el dron: ";
    for (int cliente : datos.clientes_dron) {
        cout << cliente << " ";
    }
    cout << endl;

    cout << "Matriz de traslado del camión:" << endl;
    for (const auto& fila : datos.m_traslado_camion) {
        for (double nodo : fila) {
            cout << nodo << " ";
        }
        cout << endl;
    }

    cout << "Matriz de traslado del dron:" << endl;
    for (const auto& fila : datos.m_traslado_dron) {
        for (double nodo : fila) {
            cout << nodo << " ";
        }
        cout << endl;
    }

    cout << "Número de sorties: " << datos.F << endl;
    cout << "Sorties:" << endl;
    for (const auto& sortie : datos.sorties) {
        cout << "(" << sortie.i << ", " << sortie.j << ", " << sortie.k << ")" << endl;
    }

    return 0;


}