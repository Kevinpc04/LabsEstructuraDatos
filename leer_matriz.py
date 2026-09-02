"""
Lectura eficiente de la matriz almacenada en disco.
Permite consultar valores sin cargar toda la matriz.
"""

import numpy as np
import matplotlib.pyplot as plt

N=100000

# mode="r" (solo lectura): este script únicamente consulta y visualiza
# datos, nunca los modifica, por lo que no necesita permisos de escritura
# como sí los requiere gestor_matriz.py.
matriz=np.memmap(
    "matriz_int8.dat",
    dtype=np.int8,
    mode="r",
    shape=(N,N)
)

# Consulta puntual
# Acceder a una sola posición (fila, columna) hace que NumPy lea
# únicamente ese byte del archivo en disco, sin cargar el resto
# de la matriz en memoria — esto es lo que hace viable trabajar
# con un archivo de 10 GB sin agotar la RAM.

fila=50000
columna=70000

valor=matriz[fila,columna]

print("----------------")
print("Consulta:")
print(f"Fila: {fila}")
print(f"Columna: {columna}")
print(f"Valor: {valor}")

# Lectura parcial para visualizar
# Se toma una muestra cada 1000 filas y 1000 columnas, reduciendo
# la matriz de 100,000 x 100,000 (10,000 millones de celdas) a
# una muestra de 100 x 100 (10,000 celdas). Esto permite generar
# una visualización representativa sin leer el archivo completo.

muestra=matriz[
    0:N:1000,
    0:N:1000
]

print("Tamaño muestra:")
print(muestra.shape)

# Se grafica la muestra como una imagen, donde el color de cada
# celda representa el valor almacenado (escala de color "viridis").
plt.imshow(
    muestra,
    cmap="viridis"
)

plt.colorbar()
plt.title("Muestra de matriz 100000x100000")

plt.show()