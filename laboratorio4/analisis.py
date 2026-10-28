import random
import time
import os
import math
import matplotlib.pyplot as plt
from typing import List, Tuple

# Ensure reproducibility across runs
random.seed(42)

from QuadTree import QuadTreeNode, euclidean_distance, brute_range, brute_k_nearest

Point = Tuple[float, float]

def generate_points(n: int, x_max: float = 10000.0, y_max: float = 10000.0) -> List[Point]:
    return [(random.uniform(0, x_max), random.uniform(0, y_max)) for _ in range(n)]

def benchmark_size(n_points: int, n_queries: int = 500, radius: float = 500.0, k: int = 5):
    """Run benchmarks for a given dataset size.

    Returns a dict with:
        - build_time (seconds)
        - avg_range_time (seconds)
        - avg_range_brute_time (seconds)
        - avg_knearest_time (seconds)
        - avg_knearest_brute_time (seconds)
    """
    points = generate_points(n_points)
    # ------------------- Build Quadtree -------------------
    start = time.perf_counter()
    root = QuadTreeNode((0.0, 10000.0, 0.0, 10000.0))
    for p in points:
        root.insert(p)
    build_time = time.perf_counter() - start

    # ------------------- Queries -------------------
    range_times = []
    range_brute_times = []
    knearest_times = []
    knearest_brute_times = []
    for _ in range(n_queries):
        # random query centre inside the same bounds
        centre = (random.uniform(0, 10000.0), random.uniform(0, 10000.0))
        # ---- range query ----
        t0 = time.perf_counter()
        _ = root.query_range(centre, radius)
        range_times.append(time.perf_counter() - t0)
        t0 = time.perf_counter()
        _ = brute_range(points, centre, radius)
        range_brute_times.append(time.perf_counter() - t0)
        # ---- k‑nearest query ----
        t0 = time.perf_counter()
        _ = root.k_nearest(centre, k)
        knearest_times.append(time.perf_counter() - t0)
        t0 = time.perf_counter()
        _ = brute_k_nearest(points, centre, k)
        knearest_brute_times.append(time.perf_counter() - t0)

    return {
        "size": n_points,
        "build_time": build_time,
        "avg_range_time": sum(range_times) / n_queries,
        "avg_range_brute_time": sum(range_brute_times) / n_queries,
        "avg_knearest_time": sum(knearest_times) / n_queries,
        "avg_knearest_brute_time": sum(knearest_brute_times) / n_queries,
    }

def run_full_benchmark():
    # Include very small datasets to capture the true crossover point
    sizes = [5, 10, 20, 30, 50, 75, 100, 250, 500, 1000, 2500, 5000, 10000, 20000, 50000]
    results = []
    for s in sizes:
        print(f"Benchmarking size {s}...")
        res = benchmark_size(s, n_queries=500, radius=500.0, k=5)
        results.append(res)
    # ------------------- Plotting -------------------
    os.makedirs('figuras', exist_ok=True)
    # Build time plot
    plt.figure(figsize=(8,5))
    plt.plot([r['size'] for r in results], [r['build_time'] for r in results], marker='o')
    plt.xscale('log')
    plt.xlabel('Número de puntos (log scale)')
    plt.ylabel('Tiempo de construcción (s)')
    plt.title('Tiempo de construcción del Quadtree')
    plt.grid(True, which='both', ls='--', alpha=0.5)
    plt.savefig('figuras/build_time.png')
    plt.close()
    # Range query comparison
    plt.figure(figsize=(8,5))
    plt.plot([r['size'] for r in results], [r['avg_range_time'] for r in results], label='Quadtree', marker='o')
    plt.plot([r['size'] for r in results], [r['avg_range_brute_time'] for r in results], label='Fuerza bruta', marker='x')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Número de puntos (log scale)')
    plt.ylabel('Tiempo medio de consulta (s)')
    plt.title('Búsqueda por rango (radio = 500 m)')
    plt.legend()
    plt.grid(True, which='both', ls='--', alpha=0.5)
    plt.savefig('figuras/range_query.png')
    plt.close()
    # k‑nearest query comparison
    plt.figure(figsize=(8,5))
    plt.plot([r['size'] for r in results], [r['avg_knearest_time'] for r in results], label='Quadtree', marker='o')
    plt.plot([r['size'] for r in results], [r['avg_knearest_brute_time'] for r in results], label='Fuerza bruta', marker='x')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Número de puntos (log scale)')
    plt.ylabel('Tiempo medio de consulta (s)')
    plt.title('Búsqueda de k‑vecinos más cercanos (k=5)')
    plt.legend()
    plt.grid(True, which='both', ls='--', alpha=0.5)
    plt.savefig('figuras/knearest_query.png')
    plt.close()
    # ------------------- Textual analysis -------------------
    analysis_path = os.path.join('analisis_resultados.txt')
    with open(analysis_path, 'w', encoding='utf-8') as f:
        f.write('Benchmark results (times in seconds)\n')
        f.write('Size\tBuild\tRangeQT\tRangeBF\tKNNQT\tKNNEBF\n')
        for r in results:
            f.write(f"{r['size']}\t{r['build_time']:.6f}\t{r['avg_range_time']:.6f}\t{r['avg_range_brute_time']:.6f}\t{r['avg_knearest_time']:.6f}\t{r['avg_knearest_brute_time']:.6f}\n")
        f.write('\n')
        # Find crossover points where Quadtree becomes faster than brute for each query type
        def find_cross(res_list, qt_key, bf_key):
            prev = None
            for r in res_list:
                if prev is not None:
                    # Look for transition from slower (qt > bf) to faster (qt < bf)
                    if prev[qt_key] > prev[bf_key] and r[qt_key] < r[bf_key]:
                        # Return the interval where crossing occurs
                        return f"between {prev['size']} and {r['size']}"
                prev = r
            # If never slower, report that Quadtree is always faster
            if all(r[qt_key] < r[bf_key] for r in res_list):
                return "Quadtree siempre es más rápido"
            return "No se encontró cruce dentro de los tamaños probados"
        range_cross = find_cross(results, 'avg_range_time', 'avg_range_brute_time')
        knn_cross = find_cross(results, 'avg_knearest_time', 'avg_knearest_brute_time')
        f.write(f'Range query crossover size (Quadtree faster): {range_cross}\n')
        f.write(f'k‑nearest query crossover size (Quadtree faster): {knn_cross}\n')
    print('Benchmark completado. Figuras en ./figuras y resultados en analisis_resultados.txt')

if __name__ == '__main__':
    run_full_benchmark()
