# Almacenamiento y gestión de una matriz gigante en disco

## Autor

Kevin Alexander Pantoja Castañeda

## Descripción del proyecto

Este proyecto implementa una solución para la creación, almacenamiento y manipulación de una matriz de gran tamaño:

100000 x 100000 elementos

La matriz contiene:

10.000.000.000 posiciones

Debido al tamaño de la estructura, almacenarla directamente en memoria RAM no es eficiente, por lo que se implementó almacenamiento en disco utilizando memoria mapeada mediante NumPy memmap.

# Problema planteado

Una matriz tradicional de 100000 x 100000 elementos requiere una gran cantidad de memoria RAM.

Por ejemplo:

- float64:
  80 GB aproximadamente.

- int8:
  10 GB aproximadamente.

Cargar completamente esta estructura en memoria puede generar problemas de consumo de recursos.

La solución propuesta permite trabajar con la matriz sin cargar todos los datos simultáneamente.

# Solución implementada

La matriz se almacena directamente en un archivo binario:

matriz_int8.dat

El archivo representa una matriz:

Dimensiones:
100000 x 100000

Tipo de dato:
int8

Tamaño de cada elemento:
1 byte

El acceso a la información se realiza mediante coordenadas:

A(fila,columna)

Ejemplo:

A(50000,70000)

permite consultar únicamente ese elemento sin cargar la matriz completa.

# Optimización aplicada

## 1. Reducción del consumo de RAM

La matriz no se crea utilizando un arreglo tradicional:

numpy.zeros()

porque esto requeriría almacenar toda la información en memoria.

Se utiliza:

numpy.memmap()

que permite trabajar con un archivo en disco como si fuera una matriz.

Solo se cargan en memoria los datos necesarios.

## 2. Escritura optimizada

La matriz se genera utilizando bloques.

En lugar de escribir:

100000 filas completas de una vez.

Se escriben bloques de:

2000 x 100000

Esto reduce el consumo de memoria temporal y mejora la escritura en disco.

## 3. Lectura optimizada

La matriz no se lee completamente.

Se pueden realizar:

- consultas individuales.
- lectura de zonas específicas.
- generación de muestras para visualización.

Ejemplo:

A[50000,70000]

solamente accede a una posición.

# Archivos del proyecto

## crear_matriz.py

Responsable de:

- crear la matriz de 100000 x 100000.
- reservar espacio en disco.
- generar datos por bloques.
- guardar información mediante memmap.

## leer_matriz.py

Responsable de realizar lecturas eficientes de la matriz almacenada.

Permite:

- Abrir la matriz desde disco.
- Consultar posiciones específicas.
- Extraer pequeñas zonas de la matriz.
- Crear visualizaciones mediante muestras reducidas.

La matriz completa:

100000 x 100000

no es cargada en memoria.

Ejemplos de lectura:

Consulta de una posición:

A[50000,70000]

Lectura de una zona:

Filas:
50000 - 51000

Columnas:
70000 - 71000

Visualización:

Se genera una muestra reducida mediante muestreo:

matriz[::1000,::1000]

Esto permite graficar una representación de la matriz sin cargar los 10 GB completos.

## gestor_matriz.py

Permite administrar la matriz.

Funciones:

- Consultar datos.
- Modificar valores.
- Eliminar valores.

Ejemplo:

Consultar:

A[50000,70000]

Modificar:

A[50000,70000]=50

Eliminar:

A[50000,70000]=0

## verificar_matriz.py

Permite comprobar que:

- la matriz existe.
- contiene datos.
- los valores almacenados pueden ser consultados.

# Forma de ejecución

## 1. Crear la matriz

Ejecutar:

python crear_matriz.py

Resultado esperado:

- Creación del archivo matriz_int8.dat.
- Tamaño aproximado: 10 GB.

## 2. Leer la matriz

Ejecutar:

python leer_matriz.py

Permite:

- consultar datos.
- visualizar muestras.
- analizar zonas específicas.

## 3. Gestionar la matriz

Ejecutar:

python gestor_matriz.py

Opciones disponibles:

1. Consultar dato.
2. Modificar dato.
3. Eliminar dato.
4. Salir.

## 4. Verificar contenido

Ejecutar:

python verificar_matriz.py

# Verificación del funcionamiento

Ejemplo:

Consulta:

Fila:
50000

Columna:
70000

Resultado:

A[50000,70000] = 37

Después de modificar:

A[50000,70000] = 90

La consulta posterior confirma que el cambio fue almacenado correctamente.

# Consideraciones técnicas

- La matriz mantiene dimensiones fijas.
- La eliminación de un dato se representa colocando el valor 0.
- El archivo .dat no almacena información sobre dimensiones ni tipo de dato, por lo que estos parámetros deben definirse al abrirlo.

# Conclusión

La solución permite almacenar y administrar una matriz de gran tamaño solucionando:

- consumo excesivo de RAM.
- escritura ineficiente.
- lectura innecesaria de información.  

El enfoque utilizado es similar al empleado en sistemas que manejan grandes mundos virtuales o datos científicos donde la información se almacena en disco y solamente se carga l
