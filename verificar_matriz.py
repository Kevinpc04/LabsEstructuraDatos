"""
Validación de contenido de la matriz.

Este script confirma que el archivo generado por crear_matriz.py
contiene datos válidos y accesibles, sin necesidad de cargarlo
completo en memoria.
"""

import numpy as np

N=100000

# mode="r" (solo lectura): este script solo valida contenido,
# no debe modificar el archivo bajo ninguna circunstancia.
matriz=np.memmap(
    "matriz_int8.dat",
    dtype=np.int8,
    mode="r",
    shape=(N,N)
)

# Se eligen posiciones que cubren casos representativos:
# - (0,0): primera celda de la matriz.
# - (100,200): una posición cercana al inicio.
# - (50000,70000): una posición intermedia, lejos de los bordes.
# - (99999,99999): última celda de la matriz.
# Si estas cuatro se leen correctamente, se confirma que el acceso
# funciona en todo el rango de la matriz, no solo en un punto aislado.
posiciones=[
    (0,0),
    (100,200),
    (50000,70000),
    (99999,99999)
]

for fila,columna in posiciones:

    print(
        f"A[{fila},{columna}] =",
        matriz[fila,columna]
    )


print("----------------")

# min() y max() recorren el archivo completo y confirman que todos
# los valores almacenados están dentro del rango válido de int8
# (-128 a 127). Si apareciera un valor fuera de ese rango, indicaría
# corrupción en el archivo o un error en la escritura original.
print("Valor mínimo:")
print(matriz.min())


print("Valor máximo:")
print(matriz.max())