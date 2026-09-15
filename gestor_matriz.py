"""
GESTOR DE MATRIZ GIGANTE EN DISCO

Permite administrar una matriz 100000 x 100000
almacenada mediante NumPy memmap.

Funciones:
1. Consultar un dato específico.
2. Modificar un dato específico.
3. Eliminar un dato (reemplazar por 0).
4. Verificar cambios realizados.

La matriz nunca es cargada completamente en memoria.
Solo se accede a las posiciones solicitadas.
"""

import numpy as np
import os

# Configuración de la matriz
ARCHIVO = "matriz_int8.dat"
TAMANO_MATRIZ = 100_000
TIPO_DATO = np.int8   # Debe coincidir exactamente con el tipo usado al crear el archivo
                       # (crear_matriz.py), ya que memmap no guarda esa información
                       # y lo interpretaría mal si no coincide.


def abrir_matriz():
    """
    Abre la matriz almacenada en disco en modo lectura/escritura (r+),
    necesario porque este programa no solo consulta datos sino que
    también los modifica y elimina (a diferencia de verificar_matriz.py,
    que solo lee).
    """

    if not os.path.exists(ARCHIVO):
        print("Error: No existe el archivo de matriz.")
        print("Primero debe ejecutar crear_matriz.py")
        return None

    matriz = np.memmap(
        ARCHIVO,
        dtype=TIPO_DATO,
        mode="r+",
        shape=(TAMANO_MATRIZ, TAMANO_MATRIZ)
    )

    return matriz


def consultar(matriz):
    """
    Consulta un valor en una posición específica.
    Al acceder solo a matriz[fila, columna], NumPy lee únicamente
    ese byte del archivo en disco, sin cargar el resto de la matriz.
    """

    fila = int(input("\nIngrese fila: "))
    columna = int(input("Ingrese columna: "))

    valor = matriz[fila, columna]

    print("\n------------------------")
    print("CONSULTA DE MATRIZ")
    print("------------------------")
    print(f"Posición consultada: A[{fila},{columna}]")
    print(f"Valor almacenado: {valor}")


def modificar(matriz):
    """
    Modifica un valor específico, validando que esté dentro
    del rango permitido por int8 (-128 a 127) antes de escribirlo.
    """

    fila = int(input("\nIngrese fila: "))
    columna = int(input("Ingrese columna: "))

    valor_actual = matriz[fila, columna]
    print(f"\nValor actual: {valor_actual}")

    nuevo_valor = int(input("Ingrese nuevo valor (-128 a 127): "))

    # Se valida el rango antes de escribir, porque un valor fuera
    # de rango produciría un error o un desbordamiento silencioso en int8.
    if nuevo_valor < -128 or nuevo_valor > 127:
        print("Error: valor fuera del rango int8")
        return

    matriz[fila, columna] = nuevo_valor

    # flush() escribe el cambio en disco de inmediato, en lugar de
    # dejarlo solo en el buffer de memoria hasta el cierre del programa.
    matriz.flush()

    print("\nDato actualizado correctamente")
    print(f"A[{fila},{columna}] = {matriz[fila,columna]}")


def eliminar(matriz):
    """
    Eliminar un dato en esta matriz significa reemplazarlo por el
    valor neutro 0, ya que no existe un "vacío" real en un arreglo
    numérico de tamaño fijo como este.
    """

    fila = int(input("\nIngrese fila: "))
    columna = int(input("Ingrese columna: "))

    valor = matriz[fila, columna]
    print(f"\nValor actual: {valor}")

    # Se pide confirmación porque la eliminación sobrescribe el dato
    # de forma permanente en el archivo, sin posibilidad de deshacer.
    confirmar = input("¿Desea eliminar este dato? (s/n): ")

    if confirmar.lower() == "s":
        matriz[fila, columna] = 0
        matriz.flush()

        print("\nDato eliminado correctamente")
        print(f"A[{fila},{columna}] = {matriz[fila,columna]}")
    else:
        print("Operación cancelada")


def menu():
    """
    Bucle principal del programa. Abre la matriz una sola vez al
    inicio (evitando el costo de reabrir el archivo de 10 GB en
    cada operación) y la mantiene disponible mientras el usuario
    elige opciones del menú.
    """

    matriz = abrir_matriz()

    if matriz is None:
        return

    while True:
        print("\n==============================")
        print(" GESTOR MATRIZ 100000 x 100000")
        print("==============================")

        print("1. Consultar dato\n2. Modificar dato\n3. Eliminar dato\n4. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            consultar(matriz)
        elif opcion == "2":
            modificar(matriz)
        elif opcion == "3":
            eliminar(matriz)
        elif opcion == "4":
            # Flush final por seguridad, aunque cada operación
            # ya guarda sus cambios de inmediato.
            matriz.flush()
            print("Programa finalizado")
            break
        else:
            print("Opción inválida")


if __name__ == "__main__":
    menu()