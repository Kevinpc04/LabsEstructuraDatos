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

TIPO_DATO = np.int8

def abrir_matriz():

    """
    Abre la matriz almacenada en disco.
    """

    if not os.path.exists(ARCHIVO):

        print("Error: No existe el archivo de matriz.")
        print("Primero debe ejecutar crear_matriz.py")

        return None

    matriz = np.memmap(
        ARCHIVO,
        dtype=TIPO_DATO,
        mode="r+",
        shape=(TAMANO_MATRIZ,TAMANO_MATRIZ)
    )

    return matriz

def consultar(matriz):

    """
    Consulta un valor en una posición específica.
    """

    fila = int(input("\nIngrese fila: "))
    columna = int(input("Ingrese columna: "))

    valor = matriz[fila,columna]

    print("\n------------------------")
    print("CONSULTA DE MATRIZ")
    print("------------------------")
    print(f"Posición consultada: A[{fila},{columna}]")
    print(f"Valor almacenado: {valor}")



def modificar(matriz):

    """
    Modifica un valor específico.
    """

    fila = int(input("\nIngrese fila: "))
    columna = int(input("Ingrese columna: "))

    valor_actual = matriz[fila,columna]

    print(f"\nValor actual: {valor_actual}")

    nuevo_valor = int(input("Ingrese nuevo valor (-128 a 127): "))

    if nuevo_valor < -128 or nuevo_valor > 127:

        print("Error: valor fuera del rango int8")

        return

    matriz[fila,columna] = nuevo_valor

    # Guarda inmediatamente en disco

    matriz.flush()

    print("\nDato actualizado correctamente")

    print(f"A[{fila},{columna}] = {matriz[fila,columna]}")



def eliminar(matriz):

    """
    Eliminar un dato en una matriz significa
    reemplazarlo por el valor neutro 0.
    """

    fila = int(input("\nIngrese fila: "))
    columna = int(input("Ingrese columna: "))

    valor = matriz[fila,columna]

    print(f"\nValor actual: {valor}")

    confirmar=input("¿Desea eliminar este dato? (s/n): ")

    if confirmar.lower()=="s":

        matriz[fila,columna]=0

        matriz.flush()

        print("\nDato eliminado correctamente")

        print(f"A[{fila},{columna}] = {matriz[fila,columna]}")

    else:

        print("Operación cancelada")

def menu():

    matriz = abrir_matriz()


    if matriz is None:
        return


    while True:


        print("\n==============================")
        print(" GESTOR MATRIZ 100000 x 100000")
        print("==============================")

        print("""1. Consultar dato2.\nModificar dato.\n3.Eliminar dato\n4. Salir""")

        opcion=input("Seleccione una opción: ")

        if opcion=="1":

            consultar(matriz)

        elif opcion=="2":

            modificar(matriz)

        elif opcion=="3":

            eliminar(matriz)

        elif opcion=="4":

            matriz.flush()

            print("Programa finalizado")

            break

        else:

            print("Opción inválida")

if __name__=="__main__":

    menu()