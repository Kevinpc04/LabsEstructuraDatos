import random
import time
import os
import math
import matplotlib.pyplot as plt
from typing import List, Tuple
 
# Se fija la semilla para que los resultados sean reproducibles entre ejecuciones
random.seed(42)
 
from QuadTree import NodoQuadtree, distancia_euclidiana, rango_fuerza_bruta, k_mas_cercanos_fuerza_bruta
 
Punto = Tuple[float, float]
 
def generar_puntos(n: int, x_max: float = 10000.0, y_max: float = 10000.0) -> List[Punto]:
    return [(random.uniform(0, x_max), random.uniform(0, y_max)) for _ in range(n)]
 
def benchmark_tamano(n_puntos: int, n_consultas: int = 500, radio: float = 500.0, k: int = 5):
    """Ejecuta los benchmarks para un tamaño de conjunto de datos dado.
 
    Devuelve un diccionario con:
        - tiempo_construccion (segundos)
        - tiempo_prom_rango (segundos)
        - tiempo_prom_rango_fb (segundos)
        - tiempo_prom_k_cercanos (segundos)
        - tiempo_prom_k_cercanos_fb (segundos)
    """
    puntos = generar_puntos(n_puntos)
    # ------------------- Construcción del Quadtree -------------------
    inicio = time.perf_counter()
    raiz = NodoQuadtree((0.0, 10000.0, 0.0, 10000.0))
    for p in puntos:
        raiz.insertar(p)
    tiempo_construccion = time.perf_counter() - inicio
 
    # ------------------- Consultas -------------------
    tiempos_rango = []
    tiempos_rango_fb = []
    tiempos_k_cercanos = []
    tiempos_k_cercanos_fb = []
    for _ in range(n_consultas):
        # centro de consulta aleatorio dentro de los mismos límites
        centro = (random.uniform(0, 10000.0), random.uniform(0, 10000.0))
        # ---- búsqueda por rango ----
        t0 = time.perf_counter()
        _ = raiz.consultar_rango(centro, radio)
        tiempos_rango.append(time.perf_counter() - t0)
        t0 = time.perf_counter()
        _ = rango_fuerza_bruta(puntos, centro, radio)
        tiempos_rango_fb.append(time.perf_counter() - t0)
        # ---- búsqueda de k vecinos más cercanos ----
        t0 = time.perf_counter()
        _ = raiz.k_mas_cercanos(centro, k)
        tiempos_k_cercanos.append(time.perf_counter() - t0)
        t0 = time.perf_counter()
        _ = k_mas_cercanos_fuerza_bruta(puntos, centro, k)
        tiempos_k_cercanos_fb.append(time.perf_counter() - t0)
 
    return {
        "tamano": n_puntos,
        "tiempo_construccion": tiempo_construccion,
        "tiempo_prom_rango": sum(tiempos_rango) / n_consultas,
        "tiempo_prom_rango_fb": sum(tiempos_rango_fb) / n_consultas,
        "tiempo_prom_k_cercanos": sum(tiempos_k_cercanos) / n_consultas,
        "tiempo_prom_k_cercanos_fb": sum(tiempos_k_cercanos_fb) / n_consultas,
    }
 
def ejecutar_benchmark_completo():
    # Se incluyen conjuntos muy pequeños para capturar el punto de cruce real
    tamanos = [5, 10, 20, 30, 50, 75, 100, 250, 500, 1000, 2500, 5000, 10000, 20000, 50000]
    resultados = []
    for s in tamanos:
        print(f"Evaluando tamaño {s}...")
        res = benchmark_tamano(s, n_consultas=500, radio=500.0, k=5)
        resultados.append(res)
    # ------------------- Gráficas -------------------
    os.makedirs('figuras', exist_ok=True)
    # Gráfica del tiempo de construcción
    plt.figure(figsize=(8,5))
    plt.plot([r['tamano'] for r in resultados], [r['tiempo_construccion'] for r in resultados], marker='o')
    plt.xscale('log')
    plt.xlabel('Número de puntos (escala log)')
    plt.ylabel('Tiempo de construcción (s)')
    plt.title('Tiempo de construcción del Quadtree')
    plt.grid(True, which='both', ls='--', alpha=0.5)
    plt.savefig('figuras/build_time.png')
    plt.close()
    # Comparación de la búsqueda por rango
    plt.figure(figsize=(8,5))
    plt.plot([r['tamano'] for r in resultados], [r['tiempo_prom_rango'] for r in resultados], label='Quadtree', marker='o')
    plt.plot([r['tamano'] for r in resultados], [r['tiempo_prom_rango_fb'] for r in resultados], label='Fuerza bruta', marker='x')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Número de puntos (escala log)')
    plt.ylabel('Tiempo medio de consulta (s)')
    plt.title('Búsqueda por rango (radio = 500 m)')
    plt.legend()
    plt.grid(True, which='both', ls='--', alpha=0.5)
    plt.savefig('figuras/range_query.png')
    plt.close()
    # Comparación de la búsqueda de k vecinos más cercanos
    plt.figure(figsize=(8,5))
    plt.plot([r['tamano'] for r in resultados], [r['tiempo_prom_k_cercanos'] for r in resultados], label='Quadtree', marker='o')
    plt.plot([r['tamano'] for r in resultados], [r['tiempo_prom_k_cercanos_fb'] for r in resultados], label='Fuerza bruta', marker='x')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Número de puntos (escala log)')
    plt.ylabel('Tiempo medio de consulta (s)')
    plt.title('Búsqueda de k-vecinos más cercanos (k=5)')
    plt.legend()
    plt.grid(True, which='both', ls='--', alpha=0.5)
    plt.savefig('figuras/knearest_query.png')
    plt.close()
    # ------------------- Análisis textual -------------------
    ruta_analisis = os.path.join('analisis_resultados.txt')
    with open(ruta_analisis, 'w', encoding='utf-8') as f:
        f.write('Resultados del benchmark (tiempos en segundos)\n')
        f.write('Tamaño\tConstrucción\tRangoQT\tRangoFB\tKNNQT\tKNNFB\n')
        for r in resultados:
            f.write(f"{r['tamano']}\t{r['tiempo_construccion']:.6f}\t{r['tiempo_prom_rango']:.6f}\t{r['tiempo_prom_rango_fb']:.6f}\t{r['tiempo_prom_k_cercanos']:.6f}\t{r['tiempo_prom_k_cercanos_fb']:.6f}\n")
        f.write('\n')
        # Se busca el punto de cruce donde el Quadtree pasa a ser más rápido que la fuerza bruta en cada tipo de consulta
        def encontrar_cruce(lista_res, clave_qt, clave_fb):
            anterior = None
            for r in lista_res:
                if anterior is not None:
                    # Se busca la transición de más lento (qt > fb) a más rápido (qt < fb)
                    if anterior[clave_qt] > anterior[clave_fb] and r[clave_qt] < r[clave_fb]:
                        # Se devuelve el intervalo donde ocurre el cruce
                        return f"entre {anterior['tamano']} y {r['tamano']}"
                anterior = r
            # Si nunca fue más lento, se reporta que el Quadtree siempre es más rápido
            if all(r[clave_qt] < r[clave_fb] for r in lista_res):
                return "Quadtree siempre es más rápido"
            return "No se encontró cruce dentro de los tamaños probados"
        cruce_rango = encontrar_cruce(resultados, 'tiempo_prom_rango', 'tiempo_prom_rango_fb')
        cruce_knn = encontrar_cruce(resultados, 'tiempo_prom_k_cercanos', 'tiempo_prom_k_cercanos_fb')
        f.write(f'Tamaño de cruce en búsqueda por rango (Quadtree más rápido): {cruce_rango}\n')
        f.write(f'Tamaño de cruce en búsqueda de k-vecinos más cercanos (Quadtree más rápido): {cruce_knn}\n')
    print('Benchmark completado. Figuras en ./figuras y resultados en analisis_resultados.txt')
 
if __name__ == '__main__':
    ejecutar_benchmark_completo()
