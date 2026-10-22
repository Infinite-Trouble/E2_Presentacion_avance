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



Un tabú search para tener como referencia:

https://github.com/Xavier-MaYiMing/Tabu-Search/blob/main/TS.py
