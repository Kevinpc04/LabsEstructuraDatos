import hashlib

class Nodo: #Nodo de merkle
    def __init__(self, valor_hash, dato=None):
        self.hash = valor_hash
        self.left = None
        self.right = None
        self.dato = dato

def sha256(dato): #Función que recibe la cadena de texto y devuelve el hash
    return hashlib.sha256(dato.encode()).hexdigest() 

def crear_hojas(bloques): #Función para crear hojas (hijos)

    hojas = []

    for bloque in bloques:

        bloque_hash = sha256(bloque)

        nodo = Nodo(valor_hash=bloque_hash, dato=bloque)

        hojas.append(nodo)

    return hojas


def crear_padre(izquierda, derecha): #Función para crear padre de las hojas

    combinado = izquierda.hash + derecha.hash

    hash_padre = sha256(combinado)
    padre = Nodo(hash_padre)

    padre.left = izquierda
    padre.right = derecha

    return padre


def crear_arbol(hojas): #Función que junta las hojas con sus padres para poder crear el arbol
    nivel_actual = hojas

    while len(nivel_actual) > 1:

        if len(nivel_actual) % 2 != 0: #si el número de hojas es impar duplica el ultimo

            ultimo = nivel_actual[-1]
            duplicado = Nodo(ultimo.hash, ultimo.dato)
            nivel_actual.append(duplicado)

        nuevo_nivel = []

        for i in range(0, len(nivel_actual), 2): #creo los padres

            padre = crear_padre(nivel_actual[i],nivel_actual[i+1])
            nuevo_nivel.append(padre)

        nivel_actual = nuevo_nivel

    return nivel_actual[0]

def mostrar_arbol(nodo, nivel=0): #Función que me muestra el arbol

    if nodo == None:
        return

    print("\t" * nivel + nodo.hash[:16])

    mostrar_arbol(nodo.left, nivel+1)
    mostrar_arbol(nodo.right, nivel+1)

def encontrar_hoja(nodo, dato): #Función para poder buscar una hoja

    if nodo == None:
        return None

    if nodo.dato == dato:
        return nodo

    encontrada = encontrar_hoja(nodo.left, dato)

    if encontrada:
        return encontrada

    return encontrar_hoja(nodo.right, dato)


def prueba_merkle(nodo, buscar_hash, prueba=None):

    if prueba == None:
        prueba = []


    if nodo.left == None and nodo.right == None:

        if nodo.hash == buscar_hash:
            return prueba

        return None

    # Buscar en hijo izquierdo

    izquierda = prueba_merkle(nodo.left, buscar_hash, prueba.copy())

    if izquierda != None:
        izquierda.append(("RIGHT", nodo.right.hash))
        return izquierda
    
    # Buscar en hijo derecho
    derecha = prueba_merkle(nodo.right, buscar_hash, prueba.copy())

    if derecha != None:
        derecha.append(("LEFT", nodo.left.hash))

        return derecha

    return None

def verificar_prueba(dato, prueba, raiz_original):

    hash_actual = sha256(dato)

    for direccion, hash_vecino in prueba:

        if direccion == "RIGHT":
            combinado = (hash_actual + hash_vecino)

        else:
            combinado = (hash_vecino + hash_actual)

        hash_actual = sha256(combinado)

    return hash_actual == raiz_original

if __name__ == "__main__": #Experimento del laboratorio
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

    # PRUEBA BLOQUE 3
    bloque3 = bloques[2]

    hoja3 = encontrar_hoja(raiz, bloque3)

    prueba = prueba_merkle(raiz, hoja3.hash)

    print("\nPRUEBA DE INCLUSION BLOQUE 3")

    for i in prueba:
        print(i)

    valido = verificar_prueba(bloque3, prueba, raiz.hash)
    print("\nVALIDACION:")
    print(valido)

    # DATOS FALSO
    falso = ("Transaccion 3: transferencia 999999")

    invalido = verificar_prueba(falso, prueba, raiz.hash)

    print("\nVALIDACION DATO ALTERADO:")
    print(invalido)