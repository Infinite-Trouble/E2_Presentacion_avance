#ifndef TS_H
#define TS_H

#include <iosfwd>
#include "estruct_data.h"

// Si `traza` no es nullptr, TS escribe en ese flujo un JSON con cada iteración
// (vecinos evaluados, elegido, lista tabú) para la animación. Con nullptr no registra nada.
Solucion TS(Solucion inicial, Datos &d, int iteraciones, std::ostream* traza = nullptr);

#endif
