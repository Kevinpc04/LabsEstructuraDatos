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


N = 100_000            # Dimensión de la matriz (100,000 x 100,000 = 10,000 millones de celdas)
ARCHIVO = "matriz_int8.dat"
TIPO = np.int8          # int8 usa solo 1 byte por celda (vs. 8 de float64), clave para que el archivo sea manejable (~10 GB en vez de ~80 GB)
BLOQUE = 2000           # Tamaño de bloque intermedio: evita escribir fila por fila (lento) y evita cargar todo en RAM (inviable)

inicio = time.time()    # Se mide el tiempo para verificar que la escritura por bloques es eficiente

# Creación de matriz directamente en disco.
# mode="w+" crea el archivo si no existe o lo sobreescribe si ya existe.
# memmap permite tratar el archivo como si fuera un arreglo de NumPy sin cargarlo completo en memoria.
matriz = np.memmap(ARCHIVO, dtype=TIPO, mode="w+", shape=(N, N))

print("Matriz creada:")
print(matriz.shape)

# Escritura por bloques: se generan y escriben 2000 filas a la vez
# en lugar de las 100,000 filas completas, para no saturar la RAM.
for fila in range(0, N, BLOQUE):
    # Se generan datos aleatorios en el rango exacto de int8 (-128 a 127)
    # simulando datos reales que ocuparían esas posiciones.
    bloque = np.random.randint(-128, 127, size=(BLOQUE, N), dtype=TIPO)
    matriz[fila:fila+BLOQUE, :] = bloque

# flush() obliga a escribir en disco los datos que memmap mantiene en buffer,
# garantizando que el archivo quede completo y consistente.
matriz.flush()

fin = time.time()
tamano = os.path.getsize(ARCHIVO) / (1024**3)   # Tamaño real del archivo en GB, para confirmar que corresponde a lo esperado

print("----------------------")
print("Proceso terminado")
print(f"Tiempo: {fin-inicio:.2f} segundos")     # Evidencia de eficiencia del proceso de escritura por bloques
print(f"Tamaño archivo: {tamano:.2f} GB")