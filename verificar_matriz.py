"""
Validación de contenido de la matriz.
"""


import numpy as np


N=100000


matriz=np.memmap(
    "matriz_int8.dat",
    dtype=np.int8,
    mode="r",
    shape=(N,N)
)



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

print("Valor mínimo:")
print(matriz.min())


print("Valor máximo:")
print(matriz.max())