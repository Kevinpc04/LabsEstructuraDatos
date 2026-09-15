import hashlib
 
class Nodo:
    def __init__(self, valor_hash, dato=None):
        self.hash = valor_hash
        self.left = None
        self.right = None
        self.dato = dato
 
def sha256(dato):
    return hashlib.sha256(dato.encode()).hexdigest() #crea una función que recibe el texto y entrega el hash
 
def crear_hojas(bloques): #Convierte una lista de bloques (texto) en una lista de nodos hoja.
    hojas = []
 
    for bloque in bloques:
        bloque_hash = sha256(bloque)          # Hash del contenido del bloque
        nodo = Nodo(valor_hash=bloque_hash, dato=bloque)
        hojas.append(nodo)
 
    return hojas
 
def crear_padre(izquierda, derecha): #Crea el nodo padre de dos nodos hijos (izquierdo y derecho).
    combinado = izquierda.hash + derecha.hash   # Concatenación ordenada
    hash_padre = sha256(combinado)
 
    padre = Nodo(hash_padre)
    padre.left = izquierda
    padre.right = derecha
 
    return padre
 
def crear_arbol(hojas): #Construye el árbol de Merkle completo a partir de las hojas, combinando nodos de a pares, nivel por nivel, hasta llegar a la raíz.
    nivel_actual = hojas
    # Mientras haya más de un nodo, seguimos combinando de a pares
    while len(nivel_actual) > 1:
 
        # Si el nivel tiene una cantidad impar de nodos, duplicamos
        # el último para poder emparejarlos todos
        if len(nivel_actual) % 2 != 0:
            ultimo = nivel_actual[-1]
            duplicado = Nodo(ultimo.hash, ultimo.dato)
            nivel_actual.append(duplicado)
 
        nuevo_nivel = []
 
        # Recorremos de dos en dos (i, i+1) creando el padre de cada par
        for i in range(0, len(nivel_actual), 2):
            padre = crear_padre(nivel_actual[i], nivel_actual[i + 1])
            nuevo_nivel.append(padre)
 
        # El nuevo nivel (más pequeño) pasa a ser el nivel actual
        nivel_actual = nuevo_nivel
 
    # Cuando solo queda un nodo, ese es la raíz del árbol
    return nivel_actual[0]
 
def mostrar_arbol(nodo, nivel=0):
    """
    Imprime el árbol de forma recursiva (preorden: nodo, izquierda,
    derecha), usando tabulaciones para representar la profundidad
    de cada nodo. """
    if nodo == None:
        return  # Caso base: no hay nodo, no hay nada que imprimir
 
    # Sangría proporcional al nivel (profundidad) del nodo
    print("\t" * nivel + nodo.hash[:16])
 
    # Recorrido recursivo: primero el hijo izquierdo, luego el derecho
    mostrar_arbol(nodo.left, nivel + 1)
    mostrar_arbol(nodo.right, nivel + 1)
 
def encontrar_hoja(nodo, dato): #Busca, de forma recursiva, la hoja cuyo `dato` original coincide exactamente con el buscado.
    if nodo == None:
        return None  # Caso base: llegamos más allá de una hoja, no hay coincidencia
 
    if nodo.dato == dato:
        return nodo  # Encontramos el nodo buscado
 
    # Buscar primero en el subárbol izquierdo
    encontrada = encontrar_hoja(nodo.left, dato)
 
    if encontrada:
        return encontrada
 
    # Si no estaba a la izquierda, buscar en el subárbol derecho
    return encontrar_hoja(nodo.right, dato)
 
def prueba_merkle(nodo, buscar_hash, prueba=None): #Genera la "prueba de inclusión" (Merkle proof) de una hoja específica, identificada por su hash.
    if prueba == None:
        prueba = []  # Primera llamada: se inicializa la lista vacía
 
    # Caso base: llegamos a una hoja (no tiene hijos)
    if nodo.left == None and nodo.right == None:
 
        if nodo.hash == buscar_hash:
            return prueba  # Esta es la hoja buscada: devolvemos la prueba acumulada
 
        return None  # Esta hoja no es la buscada: esta rama no sirve
 
    # Intentar encontrar la hoja en el subárbol izquierdo
    izquierda = prueba_merkle(nodo.left, buscar_hash, prueba.copy())
 
    if izquierda != None:
        # La hoja está a la izquierda -> el hermano necesario es el hijo derecho
        izquierda.append(("RIGHT", nodo.right.hash))
        return izquierda
 
    # Si no estaba a la izquierda, intentar en el subárbol derecho
    derecha = prueba_merkle(nodo.right, buscar_hash, prueba.copy())
 
    if derecha != None:
        # La hoja está a la derecha -> el hermano necesario es el hijo izquierdo
        derecha.append(("LEFT", nodo.left.hash))
        return derecha
 
    # La hoja buscada no está en ninguno de los dos subárboles
    return None
 
 
def verificar_prueba(dato, prueba, raiz_original):
    """
    Verifica si un dato pertenece al árbol de Merkle, usando
    únicamente su prueba de inclusión y el hash de la raíz original
    (sin necesidad de tener el árbol completo)
    """
    hash_actual = sha256(dato)  # Punto de partida: hash de la hoja
 
    for direccion, hash_vecino in prueba:
 
        if direccion == "RIGHT":
            # El hermano guardado corresponde al hijo derecho
            combinado = (hash_actual + hash_vecino)
        else:
            # El hermano guardado corresponde al hijo izquierdo
            combinado = (hash_vecino + hash_actual)
 
        hash_actual = sha256(combinado)  # Subimos un nivel en el árbol
 
    # Si el hash reconstruido coincide con la raíz, el dato es válido
    return hash_actual == raiz_original
 
if __name__ == "__main__":
    # ------------------------------------------------------------
    # Experimento de laboratorio: construir un árbol de Merkle con
    # 5 transacciones de ejemplo, generar una prueba de inclusión
    # para una de ellas y verificar que:
    #   a) el dato original pasa la verificación correctamente.
    #   b) un dato alterado (aunque use la misma prueba) NO pasa la
    #      verificación, demostrando la sensibilidad del hash ante
    #      cualquier cambio en el contenido.
    # ------------------------------------------------------------
 
    bloques = [
        "Transaccion 1: compra cafe",
        "Transaccion 2: pago factura",
        "Transaccion 3: transferencia 100000",
        "Transaccion 4: compra computador",
        "Transaccion 5: pago internet"]
 
    print("\nCREACIÓN ARBOL MERKLE\n")
 
    hojas = crear_hojas(bloques)
    raiz = crear_arbol(hojas)
 
    print("MERKLE ROOT:")
    print(raiz.hash)
    print("\nARBOL:")
    mostrar_arbol(raiz)
 
    # --- PRUEBA DE INCLUSIÓN PARA EL BLOQUE 3 ---
    bloque3 = bloques[2]
 
    # Ubicamos la hoja correspondiente al bloque 3 dentro del árbol
    hoja3 = encontrar_hoja(raiz, bloque3)
 
    # Generamos la prueba de inclusión (camino de hashes hermanos)
    prueba = prueba_merkle(raiz, hoja3.hash)
 
    print("\nPRUEBA DE INCLUSION BLOQUE 3")
 
    for i in prueba:
        print(i)
 
    # Verificamos con el dato ORIGINAL: debe dar True
    valido = verificar_prueba(bloque3, prueba, raiz.hash)
    print("\nVALIDACION:")
    print(valido)
 
    # --- PRUEBA CON DATO ALTERADO (usando la misma prueba) ---
    # Simulamos que alguien intenta hacer pasar un dato modificado
    # (monto de la transacción cambiado) usando la prueba original.
    falso = ("Transaccion 3: transferencia 999999")
 
    # Debe dar False, ya que el hash del dato alterado no coincide
    # con el hash que generó originalmente la prueba
    invalido = verificar_prueba(falso, prueba, raiz.hash)
 
    print("\nVALIDACION DATO ALTERADO:")
    print(invalido)