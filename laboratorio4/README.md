# Laboratorio 4 – Quadtree vs. Fuerza Bruta

## Descripción
Este proyecto compara la eficiencia de **Quadtree** (árbol espacial 2‑D) con la búsqueda lineal (fuerza bruta) para dos tipos de consultas típicas en un sistema de logística de entregas:

* **Búsqueda por rango**: encontrar todos los puntos de entrega dentro de un radio dado.
* **Vecino más cercano** (y **k‑vecinos más cercanos**): localizar el punto o los *k* puntos más próximos a una posición determinada.

Se genera un conjunto estático de 10 000 puntos de entrega (coordenadas en metros) y se realizan pruebas de rendimiento para distintos tamaños de datos.

## Estructura del repositorio
```
Laboratorio4/
├─ README.md                 
├─ requirements.txt          
├─ QuadTree.py               
├─ test.py                   
├─ analisis.py               
└─ figuras/               
```

## Instalación
```bash
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## Uso
* **Ejecutar pruebas:** `python test.py`
* **Ejecutar benchmark y generar análisis:** `python analisis.py`

## Resultados esperados
El benchmark muestra el punto de cruce donde el Quadtree supera a la fuerza bruta tanto en búsqueda por rango como en búsqueda del vecino más cercano. Dado el overhead de recursión en Python, es probable que el cruce ocurra por debajo de los 1000 puntos.

---

## Comentarios de implementación
* Capacidad máxima de cada nodo: **4** puntos.
* **MAX_DEPTH = 20** para evitar subdivisiones infinitas cuando varios puntos coinciden o están muy cercanos.
* Función `k_nearest(point, k)` mantiene un heap de los *k* mejores resultados.
* `query_range` devuelve los puntos encontrados; la función `sorted_by_distance(points, center)` permite ordenarlos.
* Semilla fija (`random.seed(42)`) garantiza reproducibilidad de los datos y de las gráficas.
