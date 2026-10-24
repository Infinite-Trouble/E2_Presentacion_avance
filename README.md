# Estructura del proyecto

1. Archivos:
instancias/Instance_* | instancias del problema a resolver
estruct_data.h | encargado de las estructuras de datos a utilizar
lectura.cpp | encargado de leer instancias
sol_inicial.cpp | genera solucion inicial con NN
makespan.cpp | evalua una solución cualquiera
TS.cpp | implementación de tabú search para encontrar una mejor solución
main.cpp | punto de entrada: ejecuta el pipeline completo
*.h | declaraciones de cada módulo

### Compilar y ejecutar (desde la raíz del proyecto):


Para cualquier instancia, donde ? es la instancia:
```
g++ -std=c++17 -O2 -Wall -Wextra *.cpp -o solver && ./solver instancias/Instance_?
```

Por ejemplo para la instancia 1 de 10:

```
g++ -std=c++17 -O2 -Wall -Wextra *.cpp -o solver && ./solver instancias/Instance_010.1_new.txt
```
Por ejemplo para la instancia 1 de 200:

```
g++ -std=c++17 -O2 -Wall -Wextra *.cpp -o solver && ./solver instancias/Instance_200.1_new.txt
```

Se debe notar que para cada instancia con N clientes las soluciones contemplan N+2 nodos.
En esto se considera que el nodo 0 y el nodo N+1 es el depósito, por lo que se contempla un ciclo completo en tanto solución.




TS: el único movimiento es introducir una sortie. Se saca un cliente j de la ruta del camión y se lo asigna a un vuelo (i,j,k), con i y k sus vecinos en la ruta. Un vecino es válido si: j es cliente, (i,j,k) está en F, tauDrone[i][j]+tauDrone[j][k] <= E, j no es lanzamiento ni recuperación de otra sortie, y i / k no repiten lanzamiento / recuperación de otra sortie (k de una sortie sí puede ser i de otra). Se elige el mejor vecino no tabú (aspiración si mejora la mejor solución), se marca la sortie como tabú y se actualiza la mejor solución. Termina a las N iteraciones o cuando no quedan vecinos.

2. Pipeline:
    a. lectura 
    b. solución inicial
    c. TS con 1000 iteraciones
    d. entrega de solución final




# Formato de solución:

Para correr el proyecto (con ? una instancia): 

        g++ -std=c++17 -O2 -Wall -Wextra *.cpp -o solver ./solver instancias/?.txt

Por ejemplo la instancia 1: 

        g++ -std=c++17 -O2 -Wall -Wextra *.cpp -o solver ./solver instancias/Instance_010.1_new.txt

O la 200:

        g++ -std=c++17 -O2 -Wall -Wextra *.cpp -o solver ./solver instancias/Instance_200.5_new.txt


Que entrega: 



# Formato de instancias

Cada instancia en el directorio de `instancias` está nombrada con el formato Instance_\<c\>.\<var\>.txt, donde \<c\> es la cantidad de clientes a servir y \<var\> es un número de identificación de variante para esa cantidad de clientes. Para cada instancia, el formato línea a línea es el siguiente:

```
<c> # Cantidad de clientes
<SL> # Tiempo de set-up del dron
<SR> # Tiempo de recuperación del dron
<E> # Tiempo que el dron puede resistir volando, en segundos
<Cdrones> # Conjunto de clientes que pueden ser atendidos por el dron
<tauTruck> # Matriz de tiempo de traslado para el camión
<tauDrone> # Matriz de tiempo de traslado para el dron
<$|F|$> # Tamaño del conjunto F
<F> # Conjunto de posibles caminos para un dron <i,j,k>
```

Por lo que las primeras 5 líneas consisten en la definición de los parámetros $c$, $SL$, $SR$ y $E$ y el conjunto $C^D$ (clientes que pueden ser atendidos por el dron). Es importante notar que las matrices de tiempos de traslado son de tamaño $(c+2)\times (c+2)$, esto debido a que se agrega el depósito al principio y al final de la matriz. Por lo que después de las 5 líneas, vienen $c+2$ líneas definiendo los tiempos de traslado del camión seguidas de otras $c+2$ líneas definiendo los tiempos de traslado del dron. Luego viene una única línea detallando el tamaño del conjunto de posibles caminos que puede hacer el dron $|F|$ y seguido de eso vienen $|F|$ líneas con las tripletas de caminos posibles (separadas por espacios).





//




Un ejemplo de tabu search para el TSP regular:
(https://www.youtube.com/watch?v=EpUV_kEPZY4)

variante de memoria de corto plazo?

optimización basada en busqueda local.
si una solución está evaluada ya, se le marca como ya revisada durante un plazo.

El procedimiento general es:

1. Solución inicial -> x
2. Generar vecindario de x -> N(x)
3. Elegir mejor vecino fuera de la lista tabú -> x'
4. Declarar x' en la lista tabú*
Esto quiere decir que no es la solución la negada, sino el movimiento. Por ejemplo en un TSP común si se tiene:
sol inicial = 1234, con swaps de consecutivos:
N(x) = 2134, 1324, 1243, 4231
Entonces si se elige 2134 como nuevo mejor, lo que se bloquea no es 2134, sino el movimiento swap (12 -> 21)
5. ¿ f(x')> f(mejor solucion actual)? mejor solución -> x'
6. ¿Se cumple criterio de parada? n iter || n iter sin mejorar solucion
6.1 repetir si 6 -> si
6.2 volver a 2 si 6 -> no




