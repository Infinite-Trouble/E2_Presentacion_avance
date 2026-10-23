#include <sstream>
#include <vector>
#include <string>
#include "lectura.h"
using namespace std;

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
