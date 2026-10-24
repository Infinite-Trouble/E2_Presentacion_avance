# TSP con camión y dron resuelto con Tabú Search

Un camión debe visitar a todos los clientes y volver al depósito. Un dron puede ayudar: el camión lo lanza en un nodo `i`, el dron atiende a un cliente `j` mientras el camión sigue su ruta, y el camión lo recupera en un nodo `k`. Ese vuelo es una *sortie* `(i, j, k)`. El objetivo es minimizar el **makespan**: el tiempo total hasta que todo termina y está de vuelta en el depósito.

El programa sigue este pipeline:

1. **Lectura** de la instancia.
2. **Solución inicial** con vecino más cercano (solo camión, sin dron).
3. **Tabú Search** con 1000 iteraciones máximo.
4. **Entrega** de la solución final: makespan, ruta del camión y vuelos del dron.

---

## Estructura del repositorio

```
instancias/              Instancias del problema (Instance_<clientes>.<variante>_new.txt)
TS/                      Código C++
  main.cpp                 punto de entrada: ejecuta el pipeline
  estruct_data.h           estructuras de datos (Datos, Solucion, Sortie)
  lectura.cpp / .h         lee una instancia
  sol_inicial.cpp / .h     solución inicial con vecino más cercano
  makespan.cpp / .h        función de evaluación
  TS.cpp / .h              Tabú Search
vishualaizer/            Visualizaciones (Python)
  comun.py                 tiene funciones comunes que necesitaan visualizador.py y animacion_ts.py , a saber: ejecutar el solver de c++, generar un mapa y leer la instancia (esto es necesario para producir un mapa aproximado de cómo estarían los nodos).
  visualizador.py          imágenes que permiten visualizar la solución inicial con la final
  animacion_ts.py          animaciones de cómo funciona el pipeline completo
  requirements.txt         dependencias de Python
  visualizaciones/         resultados generados
```


---

## Parte 1. Compilar y ejecutar el código C++

Necesitas un compilador de C++ con soporte de C++17 (`g++` o `clang++`). En macOS se instala con `xcode-select --install`.

**Paso 1.** Entra a la carpeta del código:

```
cd TS
```

**Paso 2.** Compilar:

```
g++ -std=c++17 -O2 -Wall -Wextra main.cpp lectura.cpp sol_inicial.cpp makespan.cpp TS.cpp -o solver
```


**Paso 3.** Ejecutar indicando la instancia (por ejemplo para 10 versión 1):

```
./solver ../instancias/Instance_010.1_new.txt
```


- **Makespan inicial / final:** tiempo total de la solución del vecino más cercano y de la mejor solución que encontró Tabú Search.
- **Ruta del camión:** el nodo `0` y el `n+1`  es el depósito.
- **Sorties del dron:** cada línea `(i, j, k)` es un vuelo. El dron sale del camión en `i`, atiende al cliente `j` (que ya no está en la ruta del camión) y vuelve al camión en `k`.


**Paso 3.1 {opcional}.** Ejecutar para confirmar la generación de un json que tomará animacion_ts.py (o visualizador.py) para la producción del video/gif/imágen:

```
 ./solver ../instancias/Instance_010.1_new.txt --traza jason.json
```

Requiere que se especifique que correrá en este modo (--traza) y el archivo de salida {}.json. Este proceso lo hace automático animacion_ts.py (y visualizador.py), pero en caso de que quiera verlo está disponible.


---

## Parte 2. Visualizaciones (imagen o video)

Las visualizaciones están en Python. Las instancias no traen coordenadas, solo tiempos de traslado, así que las posiciones de los nodos se reconstruyen a partir de esos tiempos. El mapa es una aproximación. Quizás para próximas entregas se podría hacer una implementación en c++ para todo.

### 2.0 Preparar el entorno de Python (una sola vez)

Desde la raíz del repositorio:

```
python3 -m venv venv
source venv/bin/activate
pip install -r vishualaizer/requirements.txt 
```


### 2.1 Imágenes 

Desde la raíz del repositorio:

```
python vishualaizer/visualizador.py instancias/Instance_010.1_new.txt
```

Genera 4 imágenes en `vishualaizer/visualizaciones/`:

| Archivo | Contenido |
|---|---|
| `..._1_mapa_inicial.png` | nodos y depósito, distinguiendo clientes aptos para dron |
| `..._2_solucion_inicial.png` | ruta inicial del camión con su makespan |
| `..._3_solucion_final.png` | ruta del camión más los vuelos del dron |
| `..._comparativa.png` | las tres anteriores lado a lado |


### 2.2 Video o GIF 

La animación muestra los nodos, la solución inicial del camión y, en cada iteración de Tabú Search: los vecinos que se generan, el mejor vecino elegido, el vuelo del dron que se agrega, el ingreso a la lista tabú y cuánto baja el makespan. animacion_ts.py genera una versión de solución que bota un json con los datos necesarios para generar el video.



**Paso 1. Generar el video.** Entra a `vishualaizer/` y ejecutar:

```
cd vishualaizer
python -W ignore -m manim -qm --media_dir visualizaciones/manim animacion_ts.py AnimacionTS
```

El MP4 queda en `vishualaizer/visualizaciones/manim/videos/animacion_ts/720p30/AnimacionTS.mp4`.

Para generar un **GIF** en vez de video, agregar `--format gif`:

```
python -W ignore -m manim -qm --format gif --media_dir visualizaciones/manim animacion_ts.py AnimacionTS
```

**Opciones** (variables de entorno, se escriben antes del comando):

| Variable | Qué hace | Por defecto |
|---|---|---|
| `TS_INSTANCIA` | instancia a animar | `Instance_010.1_new.txt` |
| `TS_MAX_ITER` | máximo de iteraciones a mostrar | todas |
| `TS_VELOCIDAD` | velocidad; `0.7` es más lento, `2` más rápido | `1` |
| `TS_FILAS_TABU` | filas visibles de la lista tabú | `5` |

Ejemplo, una instancia de 50 clientes limitada a 5 iteraciones:

```
TS_INSTANCIA=Instance_050.1_new.txt TS_MAX_ITER=5 python -W ignore -m manim -qm animacion_ts.py AnimacionTS
```

Calidad: `-ql` (480p, rápido para probar), `-qm` (720p) o `-qh` (1080p). Con instancias grandes (100 o 200 clientes) cada iteración revisa muchos vecinos y el video sería larguísimo; conviene limitar con `TS_MAX_ITER`.

La animación no reimplementa el algoritmo: `animacion_ts.py` compila `TS/solver` si hace falta y lo ejecuta con `--traza`, y `TS.cpp` escribe un JSON con cada iteración (vecinos evaluados, vecino elegido, lista tabú). Python solo dibuja ese archivo. Se puede ver la traza a mano con `./TS/solver instancias/Instance_010.1_new.txt --traza traza.json`. Sin `--traza` el solver funciona igual que siempre. El solver siempre corre sus 1000 iteraciones; `TS_MAX_ITER` solo limita cuántas se animan.

