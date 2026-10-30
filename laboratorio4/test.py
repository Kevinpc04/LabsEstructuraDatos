import random
import unittest
import math
import os
import matplotlib.pyplot as plt
from typing import List, Tuple
 
random.seed(42)
 
from QuadTree import NodoQuadtree, distancia_euclidiana, rango_fuerza_bruta, k_mas_cercanos_fuerza_bruta, ordenar_por_distancia
 
Punto = Tuple[float, float]
 
def generar_puntos(n: int, x_max: float = 10000.0, y_max: float = 10000.0) -> List[Punto]:
    """Genera *n* puntos aleatorios dentro del rectángulo [0, x_max] x [0, y_max]."""
    return [(random.uniform(0, x_max), random.uniform(0, y_max)) for _ in range(n)]
 
class TestQuadtree(unittest.TestCase):
    def setUp(self):
        # Conjunto pequeño de datos para las pruebas básicas de correctitud
        self.puntos = generar_puntos(200)
        self.raiz = NodoQuadtree((0.0, 10000.0, 0.0, 10000.0))
        for p in self.puntos:
            insertado = self.raiz.insertar(p)
            self.assertTrue(insertado, f"El punto {p} debería estar dentro de los límites de la raíz")
 
    def test_consulta_rango_correcta(self):
        centro = (5000.0, 5000.0)
        radio = 1500.0
        resultado_qt = self.raiz.consultar_rango(centro, radio)
        resultado_fb = rango_fuerza_bruta(self.puntos, centro, radio)
        # Se comparan como colecciones sin orden
        self.assertCountEqual(resultado_qt, resultado_fb)
        # También se prueba la función auxiliar de ordenamiento
        ordenado_qt = ordenar_por_distancia(resultado_qt, centro)
        ordenado_fb = ordenar_por_distancia(resultado_fb, centro)
        self.assertEqual(ordenado_qt, ordenado_fb)
 
    def test_k_cercanos_correcto(self):
        objetivo = (4000.0, 3000.0)
        k = 5
        knn_qt = self.raiz.k_mas_cercanos(objetivo, k)
        knn_fb = k_mas_cercanos_fuerza_bruta(self.puntos, objetivo, k)
        self.assertEqual(knn_qt, knn_fb)
 
    def test_cercano_unico(self):
        objetivo = (8000.0, 2000.0)
        vecino = self.raiz.mas_cercano(objetivo)
        vecino_fb = k_mas_cercanos_fuerza_bruta(self.puntos, objetivo, 1)[0]
        self.assertEqual(vecino, vecino_fb)
 
    def test_profundidad_maxima_evita_subdivision_infinita(self):
        # Se crean muchos puntos con coordenadas idénticas para forzar una subdivisión profunda
        punto_identico = (5000.0, 5000.0)
        raiz = NodoQuadtree((0.0, 10000.0, 0.0, 10000.0))
        for _ in range(50):
            raiz.insertar(punto_identico)
        # El árbol no debe superar PROFUNDIDAD_MAXIMA
        def profundidad_maxima(nodo):
            if nodo.hijos is None:
                return nodo.profundidad
            return max(profundidad_maxima(h) for h in nodo.hijos)
        profundidad = profundidad_maxima(raiz)
        self.assertLessEqual(profundidad, NodoQuadtree.PROFUNDIDAD_MAXIMA)
 
    def test_insertar_fuera_de_limites(self):
        # Se crea una raíz con límites definidos
        raiz = NodoQuadtree((0.0, 10000.0, 0.0, 10000.0))
        # Un punto fuera de los límites no debe insertarse
        punto_fuera = (15000.0, -500.0)
        insertado = raiz.insertar(punto_fuera)
        self.assertFalse(insertado, "insertar debe devolver False para puntos fuera de los límites de la raíz")
        # El árbol debe seguir vacío
        self.assertEqual(raiz.puntos, [], "La raíz no debe tener puntos después de una inserción fallida")
 
    def test_rango_radio_cero(self):
        # Se usa el conjunto de puntos que ya existe desde setUp
        centro = self.puntos[0]  # se toma un punto conocido
        # un radio 0 solo debe devolver los puntos que coinciden exactamente con el centro
        resultado = self.raiz.consultar_rango(centro, 0.0)
        # El resultado puede contener el punto del centro (si fue insertado)
        self.assertTrue(all(p == centro for p in resultado), "Un rango de radio cero solo debe devolver coincidencias exactas")
        # Se verifica que la fuerza bruta se comporte igual
        resultado_fb = rango_fuerza_bruta(self.puntos, centro, 0.0)
        self.assertCountEqual(resultado, resultado_fb)
 
    def test_consultas_arbol_vacio(self):
        raiz_vacia = NodoQuadtree((0.0, 10000.0, 0.0, 10000.0))
        centro = (5000.0, 5000.0)
        # La búsqueda por rango en un árbol vacío devuelve una lista vacía
        self.assertEqual(raiz_vacia.consultar_rango(centro, 500.0), [], "La búsqueda por rango en un árbol vacío debe devolver []")
        # El vecino más cercano en un árbol vacío devuelve None
        self.assertIsNone(raiz_vacia.mas_cercano(centro), "El más cercano en un árbol vacío debe ser None")
        # Los k vecinos más cercanos en un árbol vacío devuelven una lista vacía
        self.assertEqual(raiz_vacia.k_mas_cercanos(centro, 3), [], "Los k más cercanos en un árbol vacío deben ser []")
 
    def test_visualizacion(self):
        # Verificación visual sencilla: se genera una figura y se comprueba que se guarda sin errores
        plt.figure(figsize=(6,6))
        # Se grafican los puntos
        xs, ys = zip(*self.puntos)
        plt.scatter(xs, ys, s=10, c='blue', label='Puntos')
        # Se grafican recursivamente los límites de cada nodo
        def dibujar_limites(nodo):
            x_min, x_max, y_min, y_max = nodo.limites
            plt.plot([x_min, x_max, x_max, x_min, x_min], [y_min, y_min, y_max, y_max, y_min], 'k-')
            if nodo.hijos:
                for hijo in nodo.hijos:
                    dibujar_limites(hijo)
        dibujar_limites(self.raiz)
        plt.title('Límites del Quadtree y puntos')
        plt.legend()
        os.makedirs('figuras', exist_ok=True)
        ruta_salida = os.path.join(os.getcwd(), 'figuras', 'visualization_test.png')
        plt.savefig(ruta_salida)
        plt.close()
        self.assertTrue(os.path.exists(ruta_salida))
        # Se conserva la figura generada para incluirla en el repositorio
 
if __name__ == '__main__':
    unittest.main()
