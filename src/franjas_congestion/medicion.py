"""Experimentos de tiempo, conteo de operaciones y gráficas de la Operación 3."""

from pathlib import Path
import sys
import time
from typing import Callable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

_DIR_ACTUAL = Path(__file__).resolve().parent
if str(_DIR_ACTUAL) not in sys.path:
    sys.path.insert(0, str(_DIR_ACTUAL))

from datos import SEMILLA_POR_DEFECTO, generar_lote_series
from divide_y_venceras import (
    franja_divide_y_venceras,
    franja_divide_y_venceras_conteo,
)
from fuerza_bruta import franja_fuerza_bruta, franja_fuerza_bruta_conteo
from kadane import (
    franja_programacion_dinamica,
    franja_programacion_dinamica_conteo,
)

# Tamaños conjuntos donde fuerza bruta aún termina en pocos segundos
TAMANOS_CONJUNTOS: list[int] = [100, 250, 500, 1000, 2000, 4000]
# Tamaños grandes hasta el volumen real de 2 años (~166.000 intervalos/estación)
TAMANOS_GRANDES: list[int] = [5000, 10000, 20000, 40000, 80000, 166000]

INSTANCIAS_CONJUNTAS = 5
INSTANCIAS_GRANDES = 5
ESTACIONES_RED = 80
INTERVALOS_HISTORICO_2_ANOS = 166_440  # 2 años * 365 días * 228 intervalos/día
POTENCIA_SERVIDOR_KW = 0.5


def cronometrar_lote(
    funcion: Callable[[list[int]], tuple[int, int, int]],
    lote: list[list[int]],
    repeticiones: int,
) -> float:
    """Mide el tiempo medio por serie usando únicamente time.perf_counter.

    Args:
        funcion: estrategia a cronometrar.
        lote: lista de series pregeneradas de igual longitud n.
        repeticiones: número de repeticiones sobre el lote.

    Returns:
        Tiempo medio por serie en segundos.
    """
    inicio = time.perf_counter()
    for _ in range(repeticiones):
        for serie in lote:
            funcion(serie)
    fin = time.perf_counter()
    return (fin - inicio) / (repeticiones * len(lote))


def contar_operaciones_lote(
    funcion_conteo: Callable[[list[int]], tuple[tuple[int, int, int], int]],
    lote: list[list[int]],
) -> float:
    """Calcula el promedio de operaciones elementales sobre un lote de series.

    Args:
        funcion_conteo: variante con conteo de operaciones.
        lote: lista de series pregeneradas.

    Returns:
        Promedio de operaciones elementales por serie.
    """
    total = 0
    for serie in lote:
        _, ops = funcion_conteo(serie)
        total += ops
    return total / len(lote)


def medir_tamanos_conjuntos(
    semilla: int = SEMILLA_POR_DEFECTO,
) -> list[dict[str, float]]:
    """Mide fuerza bruta, dividir y vencer y programación dinámica en n <= 4000."""
    resultados: list[dict[str, float]] = []

    for n in TAMANOS_CONJUNTOS:
        lote = generar_lote_series(
            intervalos=n, cantidad=INSTANCIAS_CONJUNTAS, semilla=semilla
        )

        # Verificar exactitud antes de cronometrar
        for serie in lote:
            r_fb = franja_fuerza_bruta(serie)
            r_dyv = franja_divide_y_venceras(serie)
            r_pd = franja_programacion_dinamica(serie)
            assert r_fb[2] == r_dyv[2] == r_pd[2], f"Discrepancia en n={n}"

        reps_fb = 3 if n <= 1000 else 1
        reps_dyv = 15 if n <= 1000 else 5
        reps_pd = 60 if n <= 1000 else 20

        t_fb = cronometrar_lote(franja_fuerza_bruta, lote, reps_fb)
        t_dyv = cronometrar_lote(franja_divide_y_venceras, lote, reps_dyv)
        t_pd = cronometrar_lote(franja_programacion_dinamica, lote, reps_pd)

        ops_fb = contar_operaciones_lote(franja_fuerza_bruta_conteo, lote)
        ops_dyv = contar_operaciones_lote(
            franja_divide_y_venceras_conteo, lote
        )
        ops_pd = contar_operaciones_lote(
            franja_programacion_dinamica_conteo, lote
        )

        resultados.append(
            {
                "n": float(n),
                "t_fb": t_fb,
                "t_dyv": t_dyv,
                "t_pd": t_pd,
                "ops_fb": ops_fb,
                "ops_dyv": ops_dyv,
                "ops_pd": ops_pd,
            }
        )

    return resultados


def medir_tamanos_grandes(
    semilla: int = SEMILLA_POR_DEFECTO,
) -> list[dict[str, float]]:
    """Mide dividir y vencer y programación dinámica hasta n = 166.000."""
    resultados: list[dict[str, float]] = []

    for n in TAMANOS_GRANDES:
        lote = generar_lote_series(
            intervalos=n, cantidad=INSTANCIAS_GRANDES, semilla=semilla
        )

        for serie in lote:
            r_dyv = franja_divide_y_venceras(serie)
            r_pd = franja_programacion_dinamica(serie)
            assert r_dyv[2] == r_pd[2], f"Discrepancia en n={n}"

        reps_dyv = 4 if n <= 40000 else 2
        reps_pd = 20 if n <= 40000 else 10

        t_dyv = cronometrar_lote(franja_divide_y_venceras, lote, reps_dyv)
        t_pd = cronometrar_lote(franja_programacion_dinamica, lote, reps_pd)

        ops_dyv = contar_operaciones_lote(
            franja_divide_y_venceras_conteo, lote
        )
        ops_pd = contar_operaciones_lote(
            franja_programacion_dinamica_conteo, lote
        )

        resultados.append(
            {
                "n": float(n),
                "t_dyv": t_dyv,
                "t_pd": t_pd,
                "ops_dyv": ops_dyv,
                "ops_pd": ops_pd,
            }
        )

    return resultados


def generar_grafica_tiempos(
    conjuntos: list[dict[str, float]],
    grandes: list[dict[str, float]],
    ruta_salida: Path,
) -> None:
    """Genera graficas/franjas_congestion/tiempo_vs_n.png en dos paneles."""
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.2))

    n_conj = [r["n"] for r in conjuntos]
    ax1.plot(
        n_conj,
        [r["t_fb"] * 1e3 for r in conjuntos],
        "o-",
        color="#d62728",
        linewidth=2,
        label="Fuerza bruta actual Θ(n²)",
    )
    ax1.plot(
        n_conj,
        [r["t_dyv"] * 1e3 for r in conjuntos],
        "s-",
        color="#1f77b4",
        linewidth=2,
        label="Dividir y vencer Θ(n log n)",
    )
    ax1.plot(
        n_conj,
        [r["t_pd"] * 1e3 for r in conjuntos],
        "^-",
        color="#2ca02c",
        linewidth=2,
        label="Prog. dinámica (Kadane) Θ(n)",
    )
    ax1.set_title("Comparación con fuerza bruta (n = 100 a 4.000 intervalos)")
    ax1.set_xlabel("Número de intervalos de 5 min por estación (n)")
    ax1.set_ylabel("Tiempo medio por estación (ms)")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    n_gra = [r["n"] for r in grandes]
    ax2.plot(
        n_gra,
        [r["t_dyv"] * 1e3 for r in grandes],
        "s-",
        color="#1f77b4",
        linewidth=2,
        label="Dividir y vencer Θ(n log n)",
    )
    ax2.plot(
        n_gra,
        [r["t_pd"] * 1e3 for r in grandes],
        "^-",
        color="#2ca02c",
        linewidth=2,
        label="Prog. dinámica (Kadane) Θ(n)",
    )
    ax2.set_title("Escalamiento hasta histórico de 2 años (n = 5.000 a 166.000)")
    ax2.set_xlabel("Número de intervalos de 5 min por estación (n)")
    ax2.set_ylabel("Tiempo medio por estación (ms)")
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    fig.suptitle(
        "Operación 3 (Franjas de congestión): Tiempo de ejecución frente a n",
        fontsize=12,
        fontweight="bold",
    )
    fig.tight_layout()
    fig.savefig(ruta_salida, dpi=140)
    plt.close(fig)


def generar_grafica_operaciones(
    conjuntos: list[dict[str, float]],
    grandes: list[dict[str, float]],
    ruta_salida: Path,
) -> None:
    """Genera graficas/franjas_congestion/operaciones_vs_n.png."""
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.2))

    n_conj = [r["n"] for r in conjuntos]
    ax1.plot(
        n_conj,
        [r["ops_fb"] for r in conjuntos],
        "o-",
        color="#d62728",
        linewidth=2,
        label="Fuerza bruta actual Θ(n²)",
    )
    ax1.plot(
        n_conj,
        [r["ops_dyv"] for r in conjuntos],
        "s-",
        color="#1f77b4",
        linewidth=2,
        label="Dividir y vencer Θ(n log n)",
    )
    ax1.plot(
        n_conj,
        [r["ops_pd"] for r in conjuntos],
        "^-",
        color="#2ca02c",
        linewidth=2,
        label="Prog. dinámica (Kadane) Θ(n)",
    )
    ax1.set_yscale("log")
    ax1.set_title("Operaciones elementales (n = 100 a 4.000, escala log)")
    ax1.set_xlabel("Número de intervalos de 5 min por estación (n)")
    ax1.set_ylabel("Operaciones elementales por estación (escala log)")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    n_gra = [r["n"] for r in grandes]
    ax2.plot(
        n_gra,
        [r["ops_dyv"] for r in grandes],
        "s-",
        color="#1f77b4",
        linewidth=2,
        label="Dividir y vencer Θ(n log n)",
    )
    ax2.plot(
        n_gra,
        [r["ops_pd"] for r in grandes],
        "^-",
        color="#2ca02c",
        linewidth=2,
        label="Prog. dinámica (Kadane) Θ(n)",
    )
    ax2.set_title("Operaciones en tamaños grandes (n = 5.000 a 166.000)")
    ax2.set_xlabel("Número de intervalos de 5 min por estación (n)")
    ax2.set_ylabel("Operaciones elementales por estación")
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    fig.suptitle(
        "Operación 3 (Franjas de congestión): Operaciones elementales frente a n",
        fontsize=12,
        fontweight="bold",
    )
    fig.tight_layout()
    fig.savefig(ruta_salida, dpi=140)
    plt.close(fig)


def imprimir_resumen(
    conjuntos: list[dict[str, float]],
    grandes: list[dict[str, float]],
) -> None:
    """Imprime las tablas de resultados y la extrapolación a las 80 estaciones."""
    print("=== TABLA 1: TAMAÑOS CONJUNTOS (n = 100 a 4.000) ===")
    print(
        f"{'n':>6} | {'FB (ms)':>10} | {'DyV (ms)':>10} | {'PD (ms)':>10} | "
        f"{'Ops FB':>12} | {'Ops DyV':>10} | {'Ops PD':>8}"
    )
    print("-" * 78)
    for r in conjuntos:
        print(
            f"{int(r['n']):>6} | {r['t_fb']*1e3:>10.4f} | "
            f"{r['t_dyv']*1e3:>10.4f} | {r['t_pd']*1e3:>10.4f} | "
            f"{r['ops_fb']:>12.0f} | {r['ops_dyv']:>10.0f} | "
            f"{r['ops_pd']:>8.0f}"
        )

    print("\n=== TABLA 2: TAMAÑOS GRANDES (n = 5.000 a 166.000) ===")
    print(
        f"{'n':>7} | {'DyV (ms)':>10} | {'PD (ms)':>10} | "
        f"{'Ops DyV':>12} | {'Ops PD':>10}"
    )
    print("-" * 58)
    for r in grandes:
        print(
            f"{int(r['n']):>7} | {r['t_dyv']*1e3:>10.4f} | "
            f"{r['t_pd']*1e3:>10.4f} | "
            f"{r['ops_dyv']:>12.0f} | {r['ops_pd']:>10.0f}"
        )

    mapa_c = {int(r["n"]): r for r in conjuntos}
    mapa_g = {int(r["n"]): r for r in grandes}

    r2k, r4k = mapa_c[2000], mapa_c[4000]
    r40k, r80k = mapa_g[40000], mapa_g[80000]

    print("\n=== RAZONES AL DUPLICAR EL TAMAÑO (2n / n) ===")
    print(
        f"n = 2.000 -> 4.000 | FB tiempo: {r4k['t_fb']/r2k['t_fb']:.2f}x | "
        f"FB ops: {r4k['ops_fb']/r2k['ops_fb']:.2f}x"
    )
    print(
        f"n = 2.000 -> 4.000 | DyV tiempo: {r4k['t_dyv']/r2k['t_dyv']:.2f}x | "
        f"DyV ops: {r4k['ops_dyv']/r2k['ops_dyv']:.2f}x"
    )
    print(
        f"n = 2.000 -> 4.000 | PD tiempo: {r4k['t_pd']/r2k['t_pd']:.2f}x | "
        f"PD ops: {r4k['ops_pd']/r2k['ops_pd']:.2f}x"
    )
    print(
        f"n = 40.000 -> 80.000 | DyV tiempo: "
        f"{r80k['t_dyv']/r40k['t_dyv']:.2f}x | "
        f"DyV ops: {r80k['ops_dyv']/r40k['ops_dyv']:.2f}x"
    )
    print(
        f"n = 40.000 -> 80.000 | PD tiempo: "
        f"{r80k['t_pd']/r40k['t_pd']:.2f}x | "
        f"PD ops: {r80k['ops_pd']/r40k['ops_pd']:.2f}x"
    )

    # Extrapolación al histórico de 2 años (n = 166.000 por estación, 80 estaciones)
    r166k = mapa_g[166000]
    factor_cuad = (166000.0 / 4000.0) ** 2
    t_fb_1_est = r4k["t_fb"] * factor_cuad
    t_fb_80_est = ESTACIONES_RED * t_fb_1_est

    t_dyv_1_est = r166k["t_dyv"]
    t_dyv_80_est = ESTACIONES_RED * t_dyv_1_est

    t_pd_1_est = r166k["t_pd"]
    t_pd_80_est = ESTACIONES_RED * t_pd_1_est

    kwh_fb = POTENCIA_SERVIDOR_KW * (t_fb_80_est / 3600.0)
    kwh_dyv = POTENCIA_SERVIDOR_KW * (t_dyv_80_est / 3600.0)
    kwh_pd = POTENCIA_SERVIDOR_KW * (t_pd_80_est / 3600.0)

    print(
        "\n=== EXTRAPOLACIÓN AL VOLUMEN REAL (n = 166.000, 80 ESTACIONES) ==="
    )
    print(
        f"Fuerza bruta (1 estación): {t_fb_1_est:.1f} s "
        f"({t_fb_1_est/60:.2f} min) | 80 estaciones: {t_fb_80_est:.1f} s "
        f"({t_fb_80_est/3600:.2f} h) | Energía corrida: {kwh_fb:.4f} kWh "
        f"| Anual (365 noches): {kwh_fb*365:.2f} kWh/año"
    )
    print(
        f"Dividir y vencer (1 estación): {t_dyv_1_est*1e3:.2f} ms | "
        f"80 estaciones: {t_dyv_80_est:.3f} s | "
        f"Energía corrida: {kwh_dyv:.6f} kWh | "
        f"Anual (365 noches): {kwh_dyv*365:.4f} kWh/año"
    )
    print(
        f"Prog. dinámica Kadane (1 estación): {t_pd_1_est*1e3:.2f} ms | "
        f"80 estaciones: {t_pd_80_est:.3f} s | "
        f"Energía corrida: {kwh_pd:.6f} kWh | "
        f"Anual (365 noches): {kwh_pd*365:.4f} kWh/año"
    )


def ejecutar_experimentos() -> None:
    """Ejecuta las mediciones y guarda las gráficas de la Operación 3."""
    raiz_repo = Path(__file__).resolve().parents[2]
    dir_graficas = raiz_repo / "graficas" / "franjas_congestion"

    conjuntos = medir_tamanos_conjuntos(semilla=SEMILLA_POR_DEFECTO)
    grandes = medir_tamanos_grandes(semilla=SEMILLA_POR_DEFECTO)

    generar_grafica_tiempos(
        conjuntos, grandes, dir_graficas / "tiempo_vs_n.png"
    )
    generar_grafica_operaciones(
        conjuntos, grandes, dir_graficas / "operaciones_vs_n.png"
    )
    imprimir_resumen(conjuntos, grandes)
    print(f"\nGráficas guardadas en: {dir_graficas}")


if __name__ == "__main__":
    ejecutar_experimentos()
