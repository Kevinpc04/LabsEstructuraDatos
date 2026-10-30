import math
import heapq
from typing import List, Tuple, Optional
 
Punto = Tuple[float, float]
 
 
def distancia_euclidiana(p1: Punto, p2: Punto) -> float:
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])
 
 
class NodoQuadtree:
 
    CAPACIDAD_MAXIMA = 4
    PROFUNDIDAD_MAXIMA = 20
 
    def __init__(self, limites: Tuple[float, float, float, float], profundidad: int = 0):
        self.limites = limites          # (x_min, x_max, y_min, y_max)
        self.puntos: List[Punto] = []
        self.hijos: Optional[Tuple["NodoQuadtree", "NodoQuadtree", "NodoQuadtree", "NodoQuadtree"]] = None   # None = es hoja
        self.profundidad = profundidad
 
 
    def _contiene(self, punto: Punto) -> bool:
        x_min, x_max, y_min, y_max = self.limites
        return x_min <= punto[0] <= x_max and y_min <= punto[1] <= y_max
 
    def _interseca_circulo(self, centro: Punto, radio: float) -> bool:
 
        x_min, x_max, y_min, y_max = self.limites
        cx, cy = centro
        # Punto del rectángulo más cercano al centro (si el centro está dentro, es el mismo centro)
        x_cercano = max(x_min, min(cx, x_max))
        y_cercano = max(y_min, min(cy, y_max))
        return distancia_euclidiana((x_cercano, y_cercano), centro) <= radio
 
    def _subdividir(self):
        if self.profundidad >= NodoQuadtree.PROFUNDIDAD_MAXIMA:
            return
        x_min, x_max, y_min, y_max = self.limites
        x_medio = (x_min + x_max) / 2.0
        y_medio = (y_min + y_max) / 2.0
        ne = NodoQuadtree((x_medio, x_max, y_medio, y_max), self.profundidad + 1)
        no = NodoQuadtree((x_min, x_medio, y_medio, y_max), self.profundidad + 1)
        so = NodoQuadtree((x_min, x_medio, y_min, y_medio), self.profundidad + 1)
        se = NodoQuadtree((x_medio, x_max, y_min, y_medio), self.profundidad + 1)
        self.hijos = (ne, no, so, se)
        puntos_viejos = self.puntos
        self.puntos = []        # un nodo interno no guarda puntos, se reparten entre los hijos
        for pt in puntos_viejos:
            self._insertar_en_hijos(pt)
 
    def _insertar_en_hijos(self, punto: Punto) -> bool:
        if not self.hijos:
            return False
        for hijo in self.hijos:
            if hijo._contiene(punto):     # se queda con el primer hijo que lo contenga (importa para puntos en el borde)
                hijo.insertar(punto)
                return True
 
        return False
 
    def insertar(self, punto: Punto) -> bool:
        if not self._contiene(punto):
            return False
 
        if self.hijos is None:
            if len(self.puntos) < NodoQuadtree.CAPACIDAD_MAXIMA or self.profundidad >= NodoQuadtree.PROFUNDIDAD_MAXIMA:
                self.puntos.append(punto)
                return True
 
            self._subdividir()
 
        return self._insertar_en_hijos(punto)
 
    def consultar_rango(self, centro: Punto, radio: float) -> List[Punto]:
        resultado: List[Punto] = []
        if not self._interseca_circulo(centro, radio):
            return resultado        # el círculo no toca este rectángulo, se poda toda la rama
 
        for pt in self.puntos:
            if distancia_euclidiana(pt, centro) <= radio:
                resultado.append(pt)
 
        if self.hijos:
            for hijo in self.hijos:
                resultado.extend(hijo.consultar_rango(centro, radio))
        return resultado
 
    def _buscar_cercanos(self, objetivo: Punto, heap: List[Tuple[float, Punto]], k: int):
        if self.hijos:
 
            x_min, x_max, y_min, y_max = self.limites
            cx, cy = objetivo
            dx = max(x_min - cx, 0, cx - x_max)
            dy = max(y_min - cy, 0, cy - y_max)
            dist_min_cuad = dx * dx + dy * dy
            if len(heap) == k:
                mas_lejano = -heap[0][0]      # el heap guarda distancias negativas (max-heap con heapq)
                if dist_min_cuad > mas_lejano * mas_lejano:
                    return
 
        for pt in self.puntos:
            dist = distancia_euclidiana(pt, objetivo)
            if len(heap) < k:
                heapq.heappush(heap, (-dist, pt))
            else:
                if dist < -heap[0][0]:
                    heapq.heapreplace(heap, (-dist, pt))
 
        if self.hijos:
            for hijo in self.hijos:
                hijo._buscar_cercanos(objetivo, heap, k)
 
    def k_mas_cercanos(self, objetivo: Punto, k: int = 1) -> List[Punto]:
 
        if k <= 0:
            return []
        heap: List[Tuple[float, Punto]] = []
        self._buscar_cercanos(objetivo, heap, k)
 
        resultado = [pt for (_, pt) in sorted(heap, key=lambda x: -x[0])]
        return resultado
 
    def mas_cercano(self, objetivo: Punto) -> Optional[Punto]:
        puntos_cercanos = self.k_mas_cercanos(objetivo, k=1)
        return puntos_cercanos[0] if puntos_cercanos else None
 
 
def rango_fuerza_bruta(puntos: List[Punto], centro: Punto, radio: float) -> List[Punto]:
    return [p for p in puntos if distancia_euclidiana(p, centro) <= radio]
 
 
def k_mas_cercanos_fuerza_bruta(puntos: List[Punto], objetivo: Punto, k: int) -> List[Punto]:
    puntos_ordenados = sorted(puntos, key=lambda p: distancia_euclidiana(p, objetivo))
    return puntos_ordenados[:k]
 
 
def ordenar_por_distancia(puntos: List[Punto], centro: Punto) -> List[Punto]:
    return sorted(puntos, key=lambda p: distancia_euclidiana(p, centro))