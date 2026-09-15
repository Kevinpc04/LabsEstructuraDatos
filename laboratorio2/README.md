# Construcción y verificación de un Árbol de Merkle en Python

## Autor
Kevin Alexander Pantoja Castañeda

## Descripción del proyecto
Este proyecto implementa un **Árbol de Merkle (Merkle Tree)** para verificar la integridad y pertenencia de un conjunto de datos en este caso, un conjunto de transacciones mediante hashes SHA-256.

El árbol está compuesto por:

- **N bloques de datos originales** (hojas), cada uno representado por su hash.
- **Nodos intermedios**, que almacenan el hash de la concatenación de los hashes de sus dos hijos.
- Una **raíz (Merkle root)**, que resume criptográficamente todo el conjunto de datos.

## Problema planteado
Verificar si un dato específico pertenece a un conjunto grande de datos es costoso si se hace de forma directa, comparando el dato contra todos los demás elementos uno por uno.

Por ejemplo, confirmar que una transacción puntual forma parte de un bloque de miles de transacciones requeriría, en el peor de los casos, revisar el conjunto completo.

La solución propuesta permite verificar la pertenencia de un dato con un costo proporcional a **log₂(n)**, en lugar de recorrer los **n** elementos del conjunto.

## Solución implementada
Los datos se organizan en un árbol binario de hashes:

- Cada **hoja** almacena el hash SHA-256 del dato original.
- Cada **nodo padre** almacena el hash de la concatenación de los hashes de sus dos hijos.
- El proceso se repite nivel por nivel hasta obtener un único hash: la **raíz del árbol**.

La verificación de un dato se realiza mediante una **prueba de inclusión (Merkle proof)**:

```
prueba_merkle(raiz, hash_del_dato)
```

Esta prueba contiene únicamente los hashes "vecinos" necesarios para reconstruir el camino hasta la raíz, sin necesidad de conocer ni recorrer el resto de los datos.

## Optimización aplicada

**1. Verificación eficiente**

En lugar de comparar el dato contra todos los demás elementos (**n** comparaciones), solo se recalculan los hashes del camino hacia la raíz (**~log₂(n)** pasos).

**2. Construcción por niveles**

El árbol no se arma dato por dato, sino nivel por nivel:

- Se agrupan los nodos de dos en dos.
- Se genera el hash combinado de cada par.
- Se repite el proceso hasta llegar a la raíz.

Si un nivel tiene un número impar de nodos, se duplica el último para poder formar el par, evitando tener que reestructurar el árbol.

**3. Detección de alteraciones**

Cualquier cambio en un dato original modifica su hash, y ese cambio se propaga en cadena hasta la raíz. Esto permite detectar alteraciones comparando únicamente la raíz final, sin necesidad de revisar los datos completos.

## Archivos del proyecto

### merkle.py
Responsable de:

- Crear las hojas del árbol a partir de los datos originales (`crear_hojas`).
- Construir el árbol completo hasta la raíz (`crear_arbol`).
- Mostrar la estructura del árbol (`mostrar_arbol`).
- Buscar una hoja a partir de su dato original (`encontrar_hoja`).
- Generar la prueba de inclusión de un dato (`prueba_merkle`).
- Verificar una prueba de inclusión contra la raíz original (`verificar_prueba`).x1

Resultado esperado:

- Construcción del árbol a partir de 5 transacciones de ejemplo.
- Impresión de la Merkle root.
- Impresión de la estructura completa del árbol.
- Generación y muestra de la prueba de inclusión del bloque 3.
- Validación de la prueba con el dato original.
- Validación de la prueba con un dato alterado (para comprobar que falla).

## Verificación del funcionamiento

Ejemplo:

Dato original:
```
"Transaccion 3: transferencia 100000"
```

Resultado de la validación:
```
True
```

Después de alterar el dato:
```
"Transaccion 3: transferencia 999999"
```

Resultado de la validación:
```
False
```

La verificación confirma que la prueba de inclusión solo es válida para el dato exacto que generó el hash original; cualquier alteración hace que la validación falle.

## Consideraciones técnicas

- El árbol se reconstruye por completo cada vez que se ejecuta `crear_arbol`; no está pensado para actualizaciones incrementales.
- El orden de concatenación de los hashes (izquierda + derecha) debe respetarse tanto al construir el árbol como al verificar la prueba.
- Si el número de hojas es impar, el último nodo se duplica para poder formar los pares en cada nivel.

# Uso de IA

Durante el desarrollo de este laboratorio se utilizó inteligencia artificial como herramienta de apoyo para la comprensión de conceptos relacionados con árboles de Merkle, funciones hash SHA-256 y la estructura general de implementación.

El uso de IA estuvo enfocado principalmente en:

- Resolver dudas sobre la construcción de un Árbol de Merkle y el funcionamiento de los nodos.
- Apoyar la organización inicial de la estructura del programa.
- Revisar la lógica de algunas funciones relacionadas con la generación de pruebas de inclusión y verificación de hashes.
- Aclarar conceptos sobre la relación entre árboles de Merkle y Blockchain

La implementación final de la adaptación del código, pruebas y validación del funcionamiento fueron realizadas y entendidas mediante se fue desarrollando el laboratorio.

- Se uso completamente IA para la función "prueba_merkle" y "verificar_prueba" entendiaendo de manera clara su funcionamiento

## Conclusión
La solución permite verificar la integridad y pertenencia de datos individuales dentro de un conjunto grande, sin necesidad de recorrer ni almacenar todos los datos al momento de la verificación. Este enfoque es similar al empleado en sistemas de blockchain y en la sincronización eficiente de grandes volúmenes de datos, donde basta con comparar una raíz de hash para detectar cambios.
