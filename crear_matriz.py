"""
Creación optimizada de una matriz 100000 x 100000
utilizando almacenamiento en disco mediante NumPy memmap.

Objetivos:
- Evitar consumo excesivo de RAM.
- Crear datos por bloques.
- Optimizar escritura en disco.
- Optimización en la manipulación, creación, almacenamiento y lectura de datos.
"""

import numpy as np
import time
import os


N = 100_000

ARCHIVO = "matriz_int8.dat"

TIPO = np.int8

BLOQUE = 2000


inicio = time.time()


# Creación de matriz directamente en disco
matriz = np.memmap(
    ARCHIVO,
    dtype=TIPO,
    mode="w+",
    shape=(N,N)
)


print("Matriz creada:")
print(matriz.shape)


# Escritura por bloques
for fila in range(0,N,BLOQUE):

    bloque = np.random.randint(
        -128,
        127,
        size=(BLOQUE,N),
        dtype=TIPO
    )

    matriz[
        fila:fila+BLOQUE,
        :
    ] = bloque


# Fuerza la escritura en el disco

matriz.flush()


fin=time.time()


tamano=os.path.getsize(ARCHIVO)/(1024**3)


print("----------------------")
print("Proceso terminado")
print(f"Tiempo: {fin-inicio:.2f} segundos")
print(f"Tamaño archivo: {tamano:.2f} GB")