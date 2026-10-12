import random
import time
from bisect import bisect_left, bisect_right

N = 10_000
BUSQUEDAS = 100

# ---------- Datos ----------
def generar_estudiantes(n):
    nombres = ["Ana", "Carlos", "Maria", "Juan", "Laura","Pedro", "Sofia", "Luis", "Valentina", "Diego"]
    ids = random.sample(range(1000, 1000 + n * 10), n)  # IDs únicos
    return [{"id": i, "nombre":random.choice(nombres), "edad": random.randint(15, 30), "promedio": round(random.uniform(0, 10), 1)} for i in ids]

# ---------- 1. Lista (búsqueda lineal) ----------
class ListaEstudiantes:
    def __init__(self): self.datos = []
    def insertar(self, e): self.datos.append(e)              # O(1)
    def buscar(self, id_):
        for e in self.datos:                                  # O(n)
            if e["id"] == id_: return e
        return None
    def listar(self): return sorted(self.datos, key=lambda e: e["id"])  # O(n log n)
    def buscar_rango(self, lo, hi):
        # O(N + R log R). Es el mejor caso posible para una lista (escaneo optimizable).
        return sorted((e for e in self.datos if lo <= e["id"] <= hi), key=lambda e: e["id"])

# ---------- 2. ABB (todo iterativo) ----------
class NodoABB:
    __slots__ = ("est", "izq", "der")
    def __init__(self, est): self.est, self.izq, self.der = est, None, None

class ABB:
    def __init__(self): self.raiz = None
    def insertar(self, e):
        nuevo = NodoABB(e)
        if not self.raiz: self.raiz = nuevo; return
        n = self.raiz
        while True:
            if e["id"] < n.est["id"]:
                if n.izq is None: n.izq = nuevo; return
                n = n.izq
            else:
                if n.der is None: n.der = nuevo; return
                n = n.der
    def buscar(self, id_):
        n = self.raiz
        while n:
            if id_ == n.est["id"]: return n.est
            n = n.izq if id_ < n.est["id"] else n.der
        return None
    def listar(self):  # inorden iterativo con pila
        res, pila, n = [], [], self.raiz
        while pila or n:
            while n: pila.append(n); n = n.izq
            n = pila.pop(); res.append(n.est); n = n.der
        return res
    def buscar_rango(self, lo, hi):
        res, pila, n = [], [], self.raiz
        while True:
            while n:
                if n.est["id"] >= lo: pila.append(n); n = n.izq
                else: n = n.der
            if not pila: return res
            n = pila.pop()
            if n.est["id"] > hi: return res
            res.append(n.est); n = n.der
    def altura(self):
        if self.raiz is None: return 0
        max_h, pila = 0, [(self.raiz, 1)]
        while pila:
            n, h = pila.pop()
            if h > max_h: max_h = h
            if n.izq is not None: pila.append((n.izq, h + 1))
            if n.der is not None: pila.append((n.der, h + 1))
        return max_h

# ---------- 3. Árbol B+ (datos solo en hojas, hojas enlazadas) ----------
class NodoB:
    __slots__ = ("hoja", "claves", "hijos", "sig")
    def __init__(self, hoja): self.hoja, self.claves, self.hijos, self.sig = hoja, [], [], None
    # hoja: hijos[i] = estudiante de claves[i] | interno: len(hijos) = len(claves)+1

class BMas:
    def __init__(self, max_claves=32):
        self.max, self.raiz = max_claves, NodoB(True)
    def _hoja(self, id_, camino=None):
        n = self.raiz
        while not n.hoja:
            i = bisect_right(n.claves, id_)
            if camino is not None: camino.append((n, i))
            n = n.hijos[i]
        return n
    def buscar(self, id_):
        h = self._hoja(id_)
        i = bisect_left(h.claves, id_)
        return h.hijos[i] if i < len(h.claves) and h.claves[i] == id_ else None
    def insertar(self, e):
        camino = []
        n = self._hoja(e["id"], camino)
        i = bisect_left(n.claves, e["id"])
        n.claves.insert(i, e["id"]); n.hijos.insert(i, e)
        while len(n.claves) > self.max:                       # overflow -> split hacia arriba
            m, nuevo = len(n.claves) // 2, NodoB(n.hoja)
            if n.hoja:                                        # la clave se COPIA al padre
                nuevo.claves, nuevo.hijos = n.claves[m:], n.hijos[m:]
                n.claves, n.hijos = n.claves[:m], n.hijos[:m]
                nuevo.sig, n.sig = n.sig, nuevo
                sube = nuevo.claves[0]
            else:                                             # la clave SUBE (ya no queda abajo)
                sube = n.claves[m]
                nuevo.claves, nuevo.hijos = n.claves[m + 1:], n.hijos[m + 1:]
                n.claves, n.hijos = n.claves[:m], n.hijos[:m + 1]
            if not camino:                                    # se dividió la raíz: crece el árbol
                r = NodoB(False); r.claves, r.hijos = [sube], [n, nuevo]; self.raiz = r; return
            padre, j = camino.pop()
            padre.claves.insert(j, sube); padre.hijos.insert(j + 1, nuevo)
            n = padre
    def listar(self):  # hoja más a la izquierda y recorrer la lista enlazada
        n = self.raiz
        while not n.hoja: n = n.hijos[0]
        res = []
        while n: res.extend(n.hijos); n = n.sig
        return res
    def buscar_rango(self, lo, hi):
        h = self._hoja(lo)
        i = bisect_left(h.claves, lo)
        res = []
        while h is not None:
            if i < len(h.claves) and h.claves[i] > hi:
                break                       # esta hoja ya se paso del extremo superior
            claves = h.claves
            hijos = h.hijos
            while i < len(claves) and claves[i] <= hi:
                res.append(hijos[i]); i += 1
            h, i = h.sig, 0
        return res
    def altura(self):
        h, n = 0, self.raiz
        while not n.hoja: n = n.hijos[0]; h += 1
        return h + 1

# ---------- Benchmark ----------
def medir(f):
    t = time.perf_counter(); r = f(); return time.perf_counter() - t, r

def correr(titulo, estudiantes, ids_buscar):
    print(f"\n== {titulo} == ({len(estudiantes)} estudiantes, {BUSQUEDAS} búsquedas aleatorias)")
    print(f"  {'Estructura':<8}{'Inserción':>12}{'Búsqueda':>12}{'Listar':>10}")
    esperado = sorted(e["id"] for e in estudiantes)
    for nombre, cls in (("Lista", ListaEstudiantes), ("ABB", ABB), ("B+", BMas)):
        est = cls()
        t_ins, _ = medir(lambda: [est.insertar(e) for e in estudiantes])
        t_bus, _ = medir(lambda: [est.buscar(i) for i in ids_buscar])
        t_lis, lista = medir(est.listar)
        assert [e["id"] for e in lista] == esperado, f"{nombre}: listado incorrecto"
        assert all(est.buscar(i)["id"] == i for i in ids_buscar[:10])
        print(f"  {nombre:<8}{t_ins:>11.4f}s{t_bus:>11.4f}s{t_lis:>9.4f}s")

if __name__ == "__main__":
    random.seed(42)
    base = generar_estudiantes(N)
    ordenados = sorted(base, key=lambda e: e["id"])        # inserción con IDs en orden
    aleatorios = random.sample(base, len(base))            # inserción con IDs aleatorios
    ids_buscar = [e["id"] for e in random.sample(base, BUSQUEDAS)]  # mismas búsquedas para todos

    correr("IDs EN ORDEN", ordenados, ids_buscar)
    correr("IDs ALEATORIOS", aleatorios, ids_buscar)

    nuevo = {
        "id": 200000,
        "nombre": "Nuevo",
        "edad": 22,
        "promedio": 8.7}

    lista = ListaEstudiantes()
    abb = ABB()
    bplus = BMas()

    lista.insertar(nuevo)
    abb.insertar(nuevo)
    bplus.insertar(nuevo)

    print(lista.buscar(200000))
    print(abb.buscar(200000))
    print(bplus.buscar(200000))
