"""
EXPERIMENTO DE RENDIMIENTO - Parte 2 (Lista vs ABB vs Arbol B+)

Disciplina de medicion (los 6 puntos metodologicos del enunciado):
  1. >=100 repeticiones por punto, y sobre 100 objetivos DISTINTOS: se guarda el tiempo
     de cada busqueda por separado, no un promedio de un lote.
  2. Se reportan media y desviacion estandar de esas repeticiones.
  3. Se prueba con varios volumenes N. El rango de cada escenario esta justificado con
     medicion propia, no estimado a ojo (ver mas abajo el corte del ABB degenerado).
  4. Durante la medicion NO hay print(), NO hay escritura a disco y el recolector de
     basura esta DESACTIVADO, porque sus pausas meterian ruido en los tiempos.
     La generacion de datos y la construccion de las estructuras quedan FUERA del
     cronometro: el tiempo de construir se mide en un experimento aparte.
  5. Se mide el piso del cronometro: un tiempo menor que ese no es del algoritmo,
     es ruido del instrumento.
  6. Se documenta el entorno (version, hardware, semilla, fecha) al final.
"""
import csv
import gc
import math
import platform
import random
import statistics
import sys
import time
import tracemalloc
from datetime import datetime

from busqueda_estudiantes import ABB, BMas, ListaEstudiantes, generar_estudiantes

# ---------- Parametros del experimento ----------
SEMILLA = 42
REPS = 100                      # >=100 por punto
FRACCION_RANGO = 0.01           # R proporcional = 1% de N
RANGO_FIJO = 100                # R constante, para aislar el efecto de la estructura
ESCENARIOS_RANGO = (("rango_fijo", RANGO_FIJO), ("rango_prop", None))  # None = 1% de N

# Busqueda con insercion aleatoria: los N que pidio el enunciado.
N_BUSQ_ALEATORIA = (1_000, 5_000, 10_000, 50_000, 100_000)
# Busqueda con insercion ORDENADA. Ojo: el ABB aqui se convierte en una lista enlazada
# y su construccion es O(N^2). Medido: 16k tardan ~29 s, 50k ~4.7 min, 1M ~31 horas.
# Por eso este escenario usa duplicaciones exactas hasta 16k y se extrapola despues.
N_BUSQ_ORDENADA = (1_000, 2_000, 4_000, 8_000, 16_000)

# Construccion. Con insercion aleatoria si se puede llegar a 1'000.000.
N_CONSTR_ALEATORIA = (10_000, 100_000, 1_000_000)
REPS_CONSTR_ALEATORIA = {10_000: 100, 100_000: 20, 1_000_000: 3}
# Con insercion ordenada el ABB es O(N^2) y 100 repeticiones serian inviables, asi que
# se baja el numero de repeticiones en los N grandes (queda reportado en la tabla).
N_CONSTR_ORDENADA = (2_000, 4_000, 8_000, 16_000)
REPS_CONSTR_ORDENADA = {2_000: 50, 4_000: 25, 8_000: 10, 16_000: 3}

ESTRUCTURAS = (("Lista", ListaEstudiantes), ("ABB", ABB), ("B+", BMas))
SALIDA = "resultados.csv"

PISO = 0.0            # sesgo del cronometro, se calcula una vez en main()


# ---------- Utilidades de medicion ----------
def piso_del_cronometro(n=50_000):
    """Costo real de perf_counter. Se estima como la MEDIANA de intervalos vacios
    (leer el reloj dos veces seguidas): eso es exactamente el sesgo sistematico que
    hay que restarle a cada medicion. Medir el costo de una llamada completa daria un
    numero ~2x mayor, porque cada intervalo medido contiene DOS llamadas al reloj."""
    s = []
    for _ in range(n):
        t0 = time.perf_counter()
        s.append(time.perf_counter() - t0)
    return statistics.median(s)


def resumen(ts, piso=None):
    """Estadisticas de las repeticiones. Se resta el piso del cronometro a cada
    muestra ANTES de resumir: si no, el reloj se cuela como si fuera trabajo del
    algoritmo y las operaciones rapidas salen infladas (un B+ de ~1.3 us con un piso
    de 100 ns era un error sistematico del 8%)."""
    piso = PISO if piso is None else piso
    ts = [max(0.0, t - piso) for t in ts]
    return {"media": statistics.fmean(ts), "mediana": statistics.median(ts),
            "desv": statistics.stdev(ts) if len(ts) > 1 else 0.0,
            "min": min(ts), "max": max(ts), "n_reps": len(ts)}


def construir(cls, estudiantes):
    est = cls()
    for e in estudiantes:
        est.insertar(e)
    return est


def ventanas_para(ids, r, reps, rng):
    """reps ventanas, cada una devuelve EXACTAMENTE r registros (cardinalidad controlada).
    Si el tamano del rango variara, cada estructura mediria una consulta distinta y
    la comparacion no seria valida."""
    out = []
    for _ in range(reps):
        ini = rng.randrange(0, len(ids) - r + 1)
        out.append((ids[ini], ids[ini + r - 1]))
    return out


def unidades(v):
    return f"{v*1e6:.3f} us" if v < 1e-3 else (f"{v*1e3:.3f} ms" if v < 1 else f"{v:.4f} s")


# ---------- Verificacion: como sabemos que las 3 estructuras funcionan ----------
def verificar(est, datos, etiqueta, ref=None):
    """Correctitud contra una verdad de referencia calculada de forma independiente.
    Se ejecuta ANTES de medir y FUERA del cronometro. Si algo esta mal, truena aqui."""
    ref = ref or sorted(datos, key=lambda e: e["id"])
    ref_ids = [e["id"] for e in ref]
    n = len(ref)

    assert [e["id"] for e in est.listar()] == ref_ids, f"{etiqueta}: listar() no coincide"
    assert all(a == b for a, b in zip(est.listar(), ref)), f"{etiqueta}: listar() devolvio otros datos"
    for k in (0, n // 3, n // 2, n - 1):
        assert est.buscar(ref[k]["id"]) == ref[k], f"{etiqueta}: buscar({ref[k]['id']}) fallo"
    assert est.buscar(ref_ids[0] - 1) is None, f"{etiqueta}: buscar() no devuelve None"
    assert est.buscar(ref_ids[-1] + 1) is None, f"{etiqueta}: buscar() no devuelve None"
    assert hasattr(est, "buscar_rango"), f"{etiqueta}: falta buscar_rango"
    assert len(est.buscar_rango(ref_ids[0], ref_ids[-1])) == n, f"{etiqueta}: rango total"
    assert est.buscar_rango(ref[0]["id"], ref[0]["id"]) == [ref[0]], f"{etiqueta}: rango de 1 elemento"
    assert est.buscar_rango(-1, 0) == [], f"{etiqueta}: rango vacio"
    assert est.buscar_rango(ref_ids[-1], ref_ids[-1] + 10**9) == [ref[-1]], f"{etiqueta}: rango final"


def verificar_rangos(est, ref, rng, etiqueta, cuantos=8):
    """Compara buscar_rango contra un filtro lineal sobre la referencia. Si las dos
    listas coinciden, el rango es correcto para ese intervalo."""
    ids = [e["id"] for e in ref]
    n = len(ref)
    for _ in range(cuantos):
        i, j = sorted(rng.sample(range(n), 2))
        lo, hi = ids[i], ids[j]
        esperado = [e for e in ref if lo <= e["id"] <= hi]
        assert est.buscar_rango(lo, hi) == esperado, f"{etiqueta}: buscar_rango({lo},{hi}) fallo"


# ---------- Experimento 1+2: BUSQUEDA por ID y CONSULTA por RANGO ----------
def exp_medicion(ordenado, rng):
    """Mide busqueda y rango sobre la MISMA instancia de cada estructura, para no
    pagar dos veces la construccion y para que ambas graficas usen el mismo arbol."""
    etq = "ordenada" if ordenado else "aleatoria"
    ns = N_BUSQ_ORDENADA if ordenado else N_BUSQ_ALEATORIA
    f_busq, f_rango = [], []

    for n in ns:
        base = generar_estudiantes(n)                                  # fuera del cronometro
        ref = sorted(base, key=lambda e: e["id"])
        ids = [e["id"] for e in ref]
        datos = ref if ordenado else random.sample(base, n)

        # 100 objetivos DISTINTOS, los mismos para las 3 estructuras.
        objetivos = rng.sample(ids, REPS)

        for nombre, cls in ESTRUCTURAS:
            est = construir(cls, datos)                               # <- fuera del cronometro
            verificar(est, datos, f"{nombre}/{etq}/{n}", ref)
            if n <= 100_000:
                verificar_rangos(est, ref, rng, f"{nombre}/{etq}/{n}")
            altura = est.altura() if hasattr(est, "altura") else 0

            for i in objetivos[:5]:                                   # calentamiento, no medido
                est.buscar(i)
            gc.collect(); gc.disable()
            tb = []
            for i in objetivos:                                      # 100 busquedas distintas
                t0 = time.perf_counter(); est.buscar(i)
                tb.append(time.perf_counter() - t0)
            gc.enable()
            r = resumen(tb)
            r.update(experimento="busqueda", escenario=etq, n=n, estructura=nombre,
                     altura=altura, detalle=f"{REPS} busquedas de ids distintos")
            f_busq.append(r)
            linea = (f"    {nombre:<6} n={n:<7} busq={unidades(r['media']):>12} "
                     f"(desv {unidades(r['desv']):>12})  altura={altura:<6}")

            # --- dos escenarios de rango sobre la MISMA estructura ---
            for etiqueta_rango, r_fijo in ESCENARIOS_RANGO:
                R = r_fijo if r_fijo else max(1, int(n * FRACCION_RANGO))
                ventanas = ventanas_para(ids, R, REPS, rng)
                for lo, hi in ventanas[:5]:
                    est.buscar_rango(lo, hi)
                gc.collect(); gc.disable()
                tr = []
                for lo, hi in ventanas:            # 100 ventanas distintas
                    t0 = time.perf_counter(); est.buscar_rango(lo, hi)
                    tr.append(time.perf_counter() - t0)
                gc.enable()
                r2 = resumen(tr)
                r2.update(experimento=etiqueta_rango, escenario=etq, n=n,
                          estructura=nombre, altura=altura,
                          detalle=f"{REPS} ventanas, R={R} registros")
                f_rango.append(r2)
                if etiqueta_rango == "rango_fijo":
                    linea += f" rango(R={R})={unidades(r2['media'])}"
            print(linea)

            del est
        del base, ref, datos
    return f_busq, f_rango


# ---------- Experimento 3: CONSTRUCCION ----------
def exp_construccion(ordenado, rng):
    etq = "ordenada" if ordenado else "aleatoria"
    ns = N_CONSTR_ORDENADA if ordenado else N_CONSTR_ALEATORIA
    tabla_reps = REPS_CONSTR_ORDENADA if ordenado else REPS_CONSTR_ALEATORIA
    filas = []

    for n in ns:
        base = generar_estudiantes(n)
        datos = sorted(base, key=lambda e: e["id"]) if ordenado else random.sample(base, n)
        reps = tabla_reps[n]
        for nombre, cls in ESTRUCTURAS:
            ts = []
            gc.collect(); gc.disable()
            for _ in range(reps):
                t0 = time.perf_counter()
                est = cls()
                for e in datos:
                    est.insertar(e)      # <- unico momento medido
                ts.append(time.perf_counter() - t0)
                del est
            gc.enable()
            r = resumen(ts)
            r.update(experimento="construccion", escenario=etq, n=n, estructura=nombre,
                     altura=0, detalle=f"{reps} construcciones")
            filas.append(r)
            print(f"    {nombre:<6} n={n:<9} t={unidades(r['media']):>12} "
                  f"(desv {unidades(r['desv']):>12})  reps={reps}")
        del base, datos
    return filas


# ---------- Experimento 4: memoria (todo en RAM) ----------
def exp_memoria(n, rng):
    """Mide lo que CADA estructura anade encima del dataset. El dataset en si se mide
    aparte como linea base, porque los dict de los estudiantes ya existen antes de
    construir el arbol y si no se separaran las dos cosas."""
    filas = []
    gc.collect()
    tracemalloc.start()
    base = generar_estudiantes(n)
    datos = random.sample(base, n)
    act, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    filas.append({"estructura": "datos", "n": n, "pico_mb": pico / 2**20, "actual_mb": act / 2**20})
    print(f"    {'datos':<6} n={n:<9} pico={pico/2**20:8.1f} MB  (dataset de referencia)")

    for nombre, cls in ESTRUCTURAS:
        gc.collect()
        tracemalloc.start()
        est = construir(cls, datos)
        actual, pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        filas.append({"estructura": nombre, "n": n, "pico_mb": pico / 2**20,
                      "actual_mb": actual / 2**20})
        print(f"    {nombre:<6} n={n:<9} pico={pico/2**20:8.1f} MB  "
              f"remanente={actual/2**20:8.1f} MB")
        del est
        gc.collect()
    del base, datos
    return filas


# ---------- Analisis: exponente empirico ----------
def pendiente(pts):
    """Ajusta log(t) = a + b*log(N). b es el exponente REAL medido.
    O(N)->1, O(N log N)->~1.1, O(N^2)->2, O(log N)->muy pequeno."""
    xs = [math.log(n) for n, _ in pts]
    ys = [math.log(t) for _, t in pts]
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    den = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
    a = my - b * mx
    sy = math.sqrt(sum((y - my) ** 2 for y in ys) / max(1, len(ys) - 1))
    r2 = 1 - sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys)) / (len(ys) * sy ** 2) if sy else 1.0
    return a, b, r2


# ---------- Graficas ----------
def graficar(todas, memoria):
    import matplotlib
    matplotlib.use("Agg")                     # sin ventana: no interfiere con la medicion
    import matplotlib.pyplot as plt

    colores = {"Lista": "#d62728", "ABB": "#1f77b4", "B+": "#2ca02c"}

    def panel(ax, filas, exp, esc, titulo, logy=False, logx=False):
        for nombre, _ in ESTRUCTURAS:
            pts = [(f["n"], f["media"], f["desv"]) for f in filas
                   if f["experimento"] == exp and f["escenario"] == esc and f["estructura"] == nombre]
            if not pts:
                continue
            pts.sort()
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            es = [p[2] for p in pts]
            ax.errorbar(xs, ys, yerr=es, marker="o", capsize=3, color=colores[nombre], lw=1.8, ms=5)
            a, b, r2 = pendiente([(x, y) for x, y in zip(xs, ys)])
            # R^2 en la leyenda: avisa cuando un punto es ruido y la recta no describe bien
            ax.plot([], [], " ", label=f"{nombre}  b={b:.2f}  R²={r2:.3f}")
        ax.set_xscale("log" if logx else "linear")
        ax.set_yscale("log" if logy else "linear")
        ax.set_title(titulo, fontsize=11)
        ax.set_xlabel("N (estudiantes)")
        ax.set_ylabel("tiempo [s]")
        ax.grid(True, which="both", alpha=0.3, ls=":")
        ax.legend(fontsize=9)

    # --- Fig 1: busqueda, ejes lineales (lo que pide el enunciado: "la linea sube") ---
    fig, axs = plt.subplots(1, 2, figsize=(13, 5))
    panel(axs[0], todas, "busqueda", "aleatoria", "Busqueda por ID - insercion ALEATORIA")
    panel(axs[1], todas, "busqueda", "ordenada", "Busqueda por ID - insercion ORDENADA")
    fig.suptitle("G1  Tiempo de busqueda (promedio de 100, barras = desv. estandar)", fontsize=12)
    fig.tight_layout(); fig.savefig("g1_busqueda_lineal.png", dpi=130); plt.close(fig)

    # --- Fig 2: busqueda log-log, con el exponente medido ---
    fig, axs = plt.subplots(1, 2, figsize=(13, 5))
    panel(axs[0], todas, "busqueda", "aleatoria", "Busqueda - ALEATORIA (log-log)", logy=True, logx=True)
    panel(axs[1], todas, "busqueda", "ordenada", "Busqueda - ORDENADA (log-log): el ABB se degenera", logy=True, logx=True)
    fig.suptitle("G2  Escala log-log: la pendiente b es el exponente real (O(N)=1, O(N^2)=2)", fontsize=12)
    fig.tight_layout(); fig.savefig("g2_busqueda_loglog.png", dpi=130); plt.close(fig)

    # --- Fig 3: consulta por rango, donde el B+ gana ---
    fig, axs = plt.subplots(2, 2, figsize=(13, 9))
    panel(axs[0][0], todas, "rango_fijo", "aleatoria",
          "Rango con R=100 fijo - ALEATORIA (el B+ gana)", logy=True, logx=True)
    panel(axs[0][1], todas, "rango_fijo", "ordenada",
          "Rango con R=100 fijo - ORDENADA", logy=True, logx=True)
    panel(axs[1][0], todas, "rango_prop", "aleatoria",
          "Rango con R=1% de N - ALEATORIA (todos son O(N))", logy=True, logx=True)
    panel(axs[1][1], todas, "rango_prop", "ordenada",
          "Rango con R=1% de N - ORDENADA", logy=True, logx=True)
    fig.suptitle("G3  Consulta por rango: con R fijo el B+ es plano (hojas enlazadas); "
                 "con R proporcional todos pagan O(N)", fontsize=12)
    fig.tight_layout(); fig.savefig("g3_rangos.png", dpi=130); plt.close(fig)

    # --- Fig 4: construccion ---
    fig, axs = plt.subplots(1, 2, figsize=(13, 5))
    panel(axs[0], todas, "construccion", "aleatoria", "Construccion - insercion ALEATORIA", logy=True, logx=True)
    panel(axs[1], todas, "construccion", "ordenada", "Construccion - insercion ORDENADA (O(N^2) en ABB)", logy=True, logx=True)
    fig.suptitle("G4  Tiempo de construir (las listas son O(1) por elemento, el ABB degenerado es O(N^2))", fontsize=12)
    fig.tight_layout(); fig.savefig("g4_construccion.png", dpi=130); plt.close(fig)

    # --- Fig 5: memoria en RAM ---
    if memoria:
        fig, ax = plt.subplots(figsize=(7, 5))
        nombres = [m["estructura"] for m in memoria]
        picos = [m["pico_mb"] for m in memoria]
        barras = ["#999999" if x == "datos" else colores[x] for x in nombres]
        ax.bar(nombres, picos, color=barras)
        for i, v in enumerate(picos):
            ax.text(i, v, f"{v:.0f} MB", ha="center", va="bottom")
        ax.set_ylabel("memoria pico [MB]")
        ax.set_title(f"Memoria pico, N={memoria[0]['n']:,} (todo en RAM)\n"
                     "'datos' = el dataset solo; los demas = lo que anade cada estructura".replace(",", "."))
        ax.grid(True, axis="y", alpha=0.3, ls=":")
        fig.tight_layout(); fig.savefig("g5_memoria.png", dpi=130); plt.close(fig)


# ---------- Reporte ----------
def imprimir_tabla(filas, exp, esc, col_titulo, col_val, unidad=True):
    print(f"  {col_titulo:>26} | " + " | ".join(f"{n:>16}" for n, _ in ESTRUCTURAS))
    print(f"  {'-'*26}-+-" + "-+-".join("-" * 16 for _ in ESTRUCTURAS))
    for n in sorted({f["n"] for f in filas if f["experimento"] == exp and f["escenario"] == esc}):
        celdas = []
        for nombre, _ in ESTRUCTURAS:
            f = next((x for x in filas if x["experimento"] == exp and x["escenario"] == esc
                      and x["estructura"] == nombre and x["n"] == n), None)
            celdas.append(unidades(f[col_val]) if (f and unidad) else (f"{f[col_val]:.3f}" if f else "-"))
        print(f"  {n:>26,} | " + " | ".join(f"{c:>16}" for c in celdas).replace(",", "."))


def main():
    global PISO
    random.seed(SEMILLA)
    rng = random.Random(SEMILLA)
    piso = PISO = piso_del_cronometro()

    print("=" * 100)
    print("EXPERIMENTO DE RENDIMIENTO  |  Lista vs Arbol Binario de Busqueda vs Arbol B+")
    print("=" * 100)
    print(f"Fecha      : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Python     : {sys.version.split()[0]}   |  {platform.system()} {platform.release()} "
          f"({platform.machine()})")
    print(f"Procesador : {platform.processor() or 'no informado por el SO'}")
    print(f"Semilla    : {SEMILLA}   |  Repeticiones por punto: {REPS}")
    print(f"Piso del cronometro: {piso*1e9:.1f} ns (mediana de intervalos vacios).")
    print("  Se RESTA a cada medicion: el reloj no es trabajo del algoritmo.")
    print()

    filas = []
    for ordenado in (False, True):
        etq = "ORDENADA" if ordenado else "ALEATORIA"
        print(f"[1] BUSQUEDA por ID y [2] CONSULTA por RANGO -- insercion {etq}")
        fb, fr = exp_medicion(ordenado, rng)
        filas += fb + fr
        print()

    print("[3] TIEMPO DE CONSTRUCCION -- insercion ALEATORIA (incluye N=1.000.000)")
    filas += exp_construccion(False, rng)
    print()
    print("[4] TIEMPO DE CONSTRUCCION -- insercion ORDENADA (el ABB es O(N^2))")
    filas += exp_construccion(True, rng)
    print()
    print("[5] MEMORIA pico en RAM")
    memoria = exp_memoria(1_000_000, rng)
    print()

    print("=" * 100)
    print("RESULTADOS")
    print("=" * 100)
    for exp, col, titulo in (("busqueda", "media", "tiempo de BUSQUEDA por ID"),
                             ("rango_fijo", "media", "tiempo de CONSULTA por RANGO, R=100 fijo"),
                             ("rango_prop", "media", "tiempo de CONSULTA por RANGO, R=1% de N"),
                             ("construccion", "media", "tiempo de CONSTRUCCION")):
        for esc in ("aleatoria", "ordenada"):
            if any(f["experimento"] == exp and f["escenario"] == esc for f in filas):
                print(f"\n  {titulo} -- insercion {esc}")
                imprimir_tabla([f for f in filas if f["experimento"] == exp and f["escenario"] == esc],
                               exp, esc, "N", col)

    print()
    print("=" * 100)
    print("EXPONENTE EMPIRICO  b  de  log(t) = a + b*log(N)     [O(N)=1  O(N^2)=2  O(log N)=muy pequeno]")
    print("=" * 100)
    for exp in ("busqueda", "rango_fijo", "rango_prop", "construccion"):
        for esc in ("aleatoria", "ordenada"):
            sel = [f for f in filas if f["experimento"] == exp and f["escenario"] == esc]
            if len({f["n"] for f in sel}) < 2:
                continue
            print(f"\n  {exp.upper()} / insercion {esc}")
            for nombre, _ in ESTRUCTURAS:
                pts = sorted((f["n"], f["media"]) for f in sel if f["estructura"] == nombre)
                pts_med = sorted((f["n"], f["mediana"]) for f in sel if f["estructura"] == nombre)
                if len(pts) < 2:
                    continue
                a, b, r2 = pendiente(pts)
                _, bm, _ = pendiente(pts_med)
                etq = ("O(N^2)  <-- ABB degenerado" if b > 1.7 else
                       "O(N)   <-- lineal" if b > 0.8 else "sublineal (parece log(N))")
                # Si b con la media y b con la mediana se parecen, la conclusion no
                # depende de que un punto haya salido ruidoso.
                estable = "concordante" if abs(b - bm) < 0.15 else f"DIFIERE (mediana b={bm:.2f})"
                print(f"    {nombre:<6} b={b:6.3f} (mediana b={bm:5.3f}, {estable})  "
                      f"R^2={r2:5.3f}   {etq}")

    # Estimacion del ABB ordenado a 1M, a partir de la pendiente medida.
    sel = sorted((f["n"], f["media"]) for f in filas
                 if f["experimento"] == "construccion" and f["escenario"] == "ordenada"
                 and f["estructura"] == "ABB")
    if len(sel) >= 2:
        a, b, _ = pendiente(sel)
        print(f"\n  ESTIMACION (no medida, impractical): ABB con insercion ordenada y N=1.000.000")
        print(f"    t(N) ~ N^{b:.2f}  =>  t(1e6) ~ {math.exp(a + b*math.log(1e6))/3600:.1f} horas")

    graficar(filas, memoria)

    with open(SALIDA, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["experimento", "escenario", "n", "estructura", "media_s", "mediana_s",
                    "desv_s", "min_s", "max_s", "n_reps", "altura", "detalle"])
        for f in filas:
            w.writerow([f["experimento"], f["escenario"], f["n"], f["estructura"],
                        f"{f['media']:.9g}", f"{f['mediana']:.9g}", f"{f['desv']:.9g}",
                        f"{f['min']:.9g}", f"{f['max']:.9g}", f["n_reps"],
                        f.get("altura", ""), f["detalle"]])
        w.writerow([])
        w.writerow(["memoria", "escenario", "n", "estructura", "pico_mb", "remanente_mb"])
        for m in memoria:
            w.writerow(["memoria", "aleatoria", m["n"], m["estructura"],
                        f"{m['pico_mb']:.1f}", f"{m['actual_mb']:.1f}"])

    print()
    print("Graficas generadas: g1_busqueda_lineal.png, g2_busqueda_loglog.png, "
          "g3_rangos.png, g4_construccion.png, g5_memoria.png")
    print(f"Datos crudos: {SALIDA}")


if __name__ == "__main__":
    main()