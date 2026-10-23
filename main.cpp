#include <iostream>
#include <fstream>
#include "estruct_data.h"
#include "lectura.h"
#include "sol_inicial.h"
#include "makespan.h"
#include "TS.h"
using namespace std;

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

    // a. lectura
    Datos datos = leer_datos(archivo);

    // b. solución inicial
    Solucion sol = NN(datos);
    cout << "Makespan inicial: " << makespan(sol, datos) << endl;

    // c. TS con 1000 iteraciones
    Solucion final = TS(sol, datos, 1000);

    // d. entrega de solución final
    cout << "Makespan final: " << makespan(final, datos) << endl;
    cout << "Ruta del camión: ";
    for (int nodo : final.ruta_camion) {
        cout << nodo << " ";
    }
    cout << endl;   
    cout << "Sorties del dron: " << endl;
    for (const auto& s : final.vuelos_dron) {
        cout << "(" << s.i << ", " << s.j << ", " << s.k << ")" << endl;
    }
    return 0;
}
