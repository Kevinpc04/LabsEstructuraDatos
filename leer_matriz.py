"""
Lectura eficiente de la matriz almacenada en disco.
Permite consultar valores sin cargar toda la matriz.
"""

import numpy as np
import matplotlib.pyplot as plt

N=100000

matriz=np.memmap(
    "matriz_int8.dat",
    dtype=np.int8,
    mode="r",
    shape=(N,N)
)

# Consulta puntual

fila=50000
columna=70000

valor=matriz[fila,columna]

print("----------------")
print("Consulta:")
print(f"Fila: {fila}")
print(f"Columna: {columna}")
print(f"Valor: {valor}")

# Lectura parcial para visualizar

muestra=matriz[
    0:N:1000,
    0:N:1000
]

print("Tamaño muestra:")
print(muestra.shape)

plt.imshow(
    muestra,
    cmap="viridis"
)

plt.colorbar()
plt.title("Muestra de matriz 100000x100000")

plt.show()