"""Experimentos de tiempo, conteo de operaciones y gráficas del Caso 1."""

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

from datos import (
    SEMILLA_POR_DEFECTO,
    generar_lote_experimento,
    generar_muestra_usuarios_mes,
)
from estrategia import costo_minimo, costo_minimo_conteo
from exhaustivo import costo_exhaustivo, costo_exhaustivo_conteo
from regla_actual import (
    costo_regla_actual,
    costo_regla_actual_conteo,
)

TAMANOS_PEQUENOS: list[int] = [4, 6, 8, 10, 12, 16, 20]
TAMANOS_GRANDES: list[int] = [30, 100, 500, 1000, 2500, 5000, 10000, 20000]
INSTANCIAS_POR_TAMANO = 15
TARJETAS_VOLUMEN_REAL = 950_000
POTENCIA_SERVIDOR_KW = 0.5
VENTANA_OPERATIVA_S = 4 * 3600


def cronometrar_lote(
    funcion: Callable[[list[int]], int],
    lote: list[list[int]],
    repeticiones: int,
) -> float:
    """Mide el tiempo medio por instancia usando únicamente perf_counter.

    Args:
        funcion: implementación a evaluar sobre cada instancia.
        lote: lista de instancias pregeneradas del mismo tamaño d.
        repeticiones: veces que se repite el recorrido del lote.

    Returns:
        Tiempo medio de ejecución por instancia en segundos.
    """
    inicio = time.perf_counter()
    for _ in range(repeticiones):
        for instancia in lote:
            funcion(instancia)
    fin = time.perf_counter()
    return (fin - inicio) / (repeticiones * len(lote))


def contar_operaciones_lote(
    funcion_conteo: Callable[[list[int]], tuple[int, int]],
    lote: list[list[int]],
) -> float:
    """Calcula el promedio de operaciones elementales sobre un lote.

    Args:
        funcion_conteo: variante que retorna (resultado, operaciones).
        lote: lista de instancias del mismo tamaño d.

    Returns:
        Promedio de operaciones elementales por instancia.
    """
    total_ops = 0
    for instancia in lote:
        _, ops = funcion_conteo(instancia)
        total_ops += ops
    return total_ops / len(lote)


def medir_tamanos_pequenos(
    semilla: int = SEMILLA_POR_DEFECTO,
) -> list[dict[str, float]]:
    """Ejecuta el experimento conjunto con la solución exhaustiva.

    Verifica además que programación dinámica y búsqueda exhaustiva entreguen
    exactamente el mismo costo mínimo en todas las instancias medidas.

    Args:
        semilla: semilla fija de reproducibilidad.

    Returns:
        Lista de diccionarios con tiempos y operaciones para cada d pequeño.
    """
    resultados: list[dict[str, float]] = []

    for d in TAMANOS_PEQUENOS:
        lote = generar_lote_experimento(
            dias=d,
            cantidad=INSTANCIAS_POR_TAMANO,
            semilla=semilla,
            prob_viaje=0.9,
        )

        # Verificación exacta antes de cronometrar
        for inst in lote:
            val_pd = costo_minimo(inst)
            val_exh = costo_exhaustivo(inst)
            assert val_pd == val_exh, f"Discrepancia en d={d}: {inst}"

        reps_rapidas = 400
        if d <= 12:
            reps_exh = 20
        elif d <= 16:
            reps_exh = 5
        else:
            reps_exh = 2

        t_pd = cronometrar_lote(costo_minimo, lote, reps_rapidas)
        t_reg = cronometrar_lote(costo_regla_actual, lote, reps_rapidas)
        t_exh = cronometrar_lote(costo_exhaustivo, lote, reps_exh)

        ops_pd = contar_operaciones_lote(costo_minimo_conteo, lote)
        ops_reg = contar_operaciones_lote(costo_regla_actual_conteo, lote)
        ops_exh = contar_operaciones_lote(costo_exhaustivo_conteo, lote)

        dias_activos = sum(
            sum(1 for v in inst if v > 0) for inst in lote
        ) / len(lote)

        resultados.append(
            {
                "d": float(d),
                "dias_activos": dias_activos,
                "t_pd": t_pd,
                "t_regla": t_reg,
                "t_exhaustivo": t_exh,
                "ops_pd": ops_pd,
                "ops_regla": ops_reg,
                "ops_exhaustivo": ops_exh,
            }
        )

    return resultados


def medir_tamanos_grandes(
    semilla: int = SEMILLA_POR_DEFECTO,
) -> list[dict[str, float]]:
    """Mide estrategia y regla actual en tamaños grandes para extrapolar.

    Args:
        semilla: semilla fija de reproducibilidad.

    Returns:
        Lista de diccionarios con tiempos y operaciones en d grandes.
    """
    resultados: list[dict[str, float]] = []

    for d in TAMANOS_GRANDES:
        lote = generar_lote_experimento(
            dias=d,
            cantidad=INSTANCIAS_POR_TAMANO,
            semilla=semilla,
            prob_viaje=0.9,
        )

        if d <= 100:
            reps = 400
        elif d <= 2500:
            reps = 80
        else:
            reps = 25

        t_pd = cronometrar_lote(costo_minimo, lote, reps)
        t_reg = cronometrar_lote(costo_regla_actual, lote, reps)

        ops_pd = contar_operaciones_lote(costo_minimo_conteo, lote)
        ops_reg = contar_operaciones_lote(costo_regla_actual_conteo, lote)

        resultados.append(
            {
                "d": float(d),
                "t_pd": t_pd,
                "t_regla": t_reg,
                "ops_pd": ops_pd,
                "ops_regla": ops_reg,
            }
        )

    return resultados


def medir_mejora_economica(
    semilla: int = SEMILLA_POR_DEFECTO,
) -> dict[int, dict[str, float]]:
    """Mide cuánto mejora el cobro frente a la regla actual en meses reales.

    Args:
        semilla: semilla fija para reproducir la muestra de tarjetas.

    Returns:
        Diccionario indexado por duración del mes (30 y 31 días) con las
        métricas de sobrecobro evitado.
    """
    resumen: dict[int, dict[str, float]] = {}

    for dias_mes in (30, 31):
        tarjetas = generar_muestra_usuarios_mes(
            cantidad=5000,
            dias_mes=dias_mes,
            semilla=semilla,
        )
        afectadas = 0
        sobrecobro_total = 0
        max_sobrecobro = 0

        for viajes in tarjetas:
            opt = costo_minimo(viajes)
            reg = costo_regla_actual(viajes)
            dif = reg - opt
            if dif > 0:
                afectadas += 1
                sobrecobro_total += dif
                if dif > max_sobrecobro:
                    max_sobrecobro = dif

        n_muestra = len(tarjetas)
        porcentaje = (afectadas / n_muestra) * 100.0
        prom_afectada = sobrecobro_total / afectadas if afectadas > 0 else 0.0
        prom_global = sobrecobro_total / n_muestra
        proyeccion_sitvm = prom_global * TARJETAS_VOLUMEN_REAL

        resumen[dias_mes] = {
            "porcentaje_afectadas": porcentaje,
            "promedio_por_afectada": prom_afectada,
            "promedio_por_tarjeta": prom_global,
            "max_sobrecobro": float(max_sobrecobro),
            "proyeccion_mensual_cop": proyeccion_sitvm,
        }

    return resumen


def generar_grafica_tiempos(
    pequenos: list[dict[str, float]],
    grandes: list[dict[str, float]],
    ruta_salida: Path,
) -> None:
    """Genera la gráfica tiempo_vs_n.png con contraste y escala grande.

    Args:
        pequenos: mediciones en d pequeños (con solución exhaustiva).
        grandes: mediciones en d grandes (estrategia y regla actual).
        ruta_salida: archivo PNG de destino.
    """
    d_peq = [r["d"] for r in pequenos]
    t_pd_peq_ms = [r["t_pd"] * 1e3 for r in pequenos]
    t_reg_peq_ms = [r["t_regla"] * 1e3 for r in pequenos]
    t_exh_peq_ms = [r["t_exhaustivo"] * 1e3 for r in pequenos]

    d_gra = [r["d"] for r in grandes]
    t_pd_gra_ms = [r["t_pd"] * 1e3 for r in grandes]
    t_reg_gra_ms = [r["t_regla"] * 1e3 for r in grandes]

    fig, (ax_izq, ax_der) = plt.subplots(1, 2, figsize=(13.5, 5.4), dpi=200)
    fig.suptitle(
        "Liquidación del tope tarifario: tiempo medio frente al tamaño d",
        fontsize=13,
        fontweight="bold",
        y=0.98,
    )

    # Panel izquierdo
    ax_izq.plot(
        d_peq,
        t_exh_peq_ms,
        marker="^",
        linewidth=2.2,
        color="#c0392b",
        label="Exhaustivo (exponencial)",
    )
    ax_izq.plot(
        d_peq,
        t_pd_peq_ms,
        marker="o",
        linewidth=2.2,
        color="#1f77b4",
        label="Estrategia PD — Θ(d)",
    )
    ax_izq.plot(
        d_peq,
        t_reg_peq_ms,
        marker="s",
        linestyle="--",
        linewidth=1.9,
        color="#2ca02c",
        label="Regla actual — Θ(d)",
    )
    ax_izq.set_title("a) Contraste con búsqueda exhaustiva (d = 4 a 20 días)")
    ax_izq.set_xlabel("Tamaño de entrada d (días del periodo)")
    ax_izq.set_ylabel("Tiempo medio de ejecución por instancia (ms)")
    ax_izq.set_xticks(d_peq)
    ax_izq.grid(True, linestyle=":", alpha=0.6)
    ax_izq.legend(loc="upper left", frameon=True)

    # Panel derecho
    ax_der.plot(
        d_gra,
        t_pd_gra_ms,
        marker="o",
        linewidth=2.2,
        color="#1f77b4",
        label="Estrategia PD — Θ(d)",
    )
    ax_der.plot(
        d_gra,
        t_reg_gra_ms,
        marker="s",
        linestyle="--",
        linewidth=1.9,
        color="#2ca02c",
        label="Regla actual — Θ(d)",
    )
    ax_der.set_title(
        "b) Escalamiento lineal para extrapolación (d hasta 20.000)"
    )
    ax_der.set_xlabel("Tamaño de entrada d (días del periodo)")
    ax_der.set_ylabel("Tiempo medio de ejecución por instancia (ms)")
    ax_der.grid(True, linestyle=":", alpha=0.6)
    ax_der.legend(loc="upper left", frameon=True)

    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.94))
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta_salida)
    plt.close(fig)


def generar_grafica_operaciones(
    pequenos: list[dict[str, float]],
    grandes: list[dict[str, float]],
    ruta_salida: Path,
) -> None:
    """Genera la gráfica operaciones_vs_n.png para operaciones elementales.

    Args:
        pequenos: mediciones en d pequeños (con solución exhaustiva).
        grandes: mediciones en d grandes (estrategia y regla actual).
        ruta_salida: archivo PNG de destino.
    """
    d_peq = [r["d"] for r in pequenos]
    ops_pd_peq = [r["ops_pd"] for r in pequenos]
    ops_reg_peq = [r["ops_regla"] for r in pequenos]
    ops_exh_peq = [r["ops_exhaustivo"] for r in pequenos]

    d_gra = [r["d"] for r in grandes]
    ops_pd_gra = [r["ops_pd"] for r in grandes]
    ops_reg_gra = [r["ops_regla"] for r in grandes]

    fig, (ax_izq, ax_der) = plt.subplots(1, 2, figsize=(13.5, 5.4), dpi=200)
    fig.suptitle(
        "Liquidación del tope tarifario: operaciones elementales frente a d",
        fontsize=13,
        fontweight="bold",
        y=0.98,
    )

    ax_izq.plot(
        d_peq,
        ops_exh_peq,
        marker="^",
        linewidth=2.2,
        color="#c0392b",
        label="Exhaustivo (combinaciones evaluadas)",
    )
    ax_izq.plot(
        d_peq,
        ops_pd_peq,
        marker="o",
        linewidth=2.2,
        color="#1f77b4",
        label="Estrategia PD — Θ(d)",
    )
    ax_izq.plot(
        d_peq,
        ops_reg_peq,
        marker="s",
        linestyle="--",
        linewidth=1.9,
        color="#2ca02c",
        label="Regla actual — Θ(d)",
    )
    ax_izq.set_title("a) Contraste con búsqueda exhaustiva (d = 4 a 20 días)")
    ax_izq.set_xlabel("Tamaño de entrada d (días del periodo)")
    ax_izq.set_ylabel("Operaciones elementales medias (evaluaciones)")
    ax_izq.set_xticks(d_peq)
    ax_izq.grid(True, linestyle=":", alpha=0.6)
    ax_izq.legend(loc="upper left", frameon=True)

    ax_der.plot(
        d_gra,
        ops_pd_gra,
        marker="o",
        linewidth=2.2,
        color="#1f77b4",
        label="Estrategia PD — Θ(d)",
    )
    ax_der.plot(
        d_gra,
        ops_reg_gra,
        marker="s",
        linestyle="--",
        linewidth=1.9,
        color="#2ca02c",
        label="Regla actual — Θ(d)",
    )
    ax_der.set_title("b) Crecimiento lineal de operaciones (d hasta 20.000)")
    ax_der.set_xlabel("Tamaño de entrada d (días del periodo)")
    ax_der.set_ylabel("Operaciones elementales medias (evaluaciones)")
    ax_der.grid(True, linestyle=":", alpha=0.6)
    ax_der.legend(loc="upper left", frameon=True)

    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.94))
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta_salida)
    plt.close(fig)


def imprimir_resumen(
    pequenos: list[dict[str, float]],
    grandes: list[dict[str, float]],
    mejora: dict[int, dict[str, float]],
) -> None:
    """Imprime las tablas de resultados, razones de duplicación y energía.

    Args:
        pequenos: resultados de tamaños cortos.
        grandes: resultados de tamaños grandes.
        mejora: métricas de ahorro para los usuarios en meses de 30 y 31 días.
    """
    print("=== TABLA 1: TAMAÑOS PEQUEÑOS (d = 4 a 20) ===")
    encabezado_1 = (
        f"{'d':>4} | {'m_act':>5} | {'t_PD (µs)':>10} | {'t_Reg (µs)':>10} | "
        f"{'t_Exh (ms)':>11} | {'Ops PD':>8} | {'Ops Reg':>8} | "
        f"{'Ops Exh':>12}"
    )
    print(encabezado_1)
    print("-" * len(encabezado_1))
    for r in pequenos:
        print(
            f"{int(r['d']):>4} | {r['dias_activos']:>5.1f} | "
            f"{r['t_pd'] * 1e6:>10.2f} | {r['t_regla'] * 1e6:>10.2f} | "
            f"{r['t_exhaustivo'] * 1e3:>11.4f} | {r['ops_pd']:>8.1f} | "
            f"{r['ops_regla']:>8.1f} | {r['ops_exhaustivo']:>12.1f}"
        )

    print("\n=== TABLA 2: TAMAÑOS GRANDES (d = 30 a 20.000) ===")
    encabezado_2 = (
        f"{'d':>7} | {'t_PD (ms)':>10} | {'t_Reg (ms)':>10} | "
        f"{'Ops PD':>10} | {'Ops Reg':>10}"
    )
    print(encabezado_2)
    print("-" * len(encabezado_2))
    for r in grandes:
        print(
            f"{int(r['d']):>7} | {r['t_pd'] * 1e3:>10.4f} | "
            f"{r['t_regla'] * 1e3:>10.4f} | "
            f"{r['ops_pd']:>10.1f} | {r['ops_regla']:>10.1f}"
        )

    # Parejas (d, 2d): (10 -> 20) y (10.000 -> 20.000)
    mapa_peq = {int(r["d"]): r for r in pequenos}
    mapa_gra = {int(r["d"]): r for r in grandes}
    r10, r20 = mapa_peq[10], mapa_peq[20]
    r10k, r20k = mapa_gra[10000], mapa_gra[20000]

    print("\n=== RAZONES AL DUPLICAR EL TAMAÑO (2d / d) ===")
    print(
        f"d = 10 -> 20 | Tiempo PD: {r20['t_pd'] / r10['t_pd']:.2f}x | "
        f"Ops PD: {r20['ops_pd'] / r10['ops_pd']:.2f}x"
    )
    print(
        f"d = 10 -> 20 | Tiempo Regla: "
        f"{r20['t_regla'] / r10['t_regla']:.2f}x | "
        f"Ops Regla: {r20['ops_regla'] / r10['ops_regla']:.2f}x"
    )
    print(
        f"d = 10 -> 20 | Tiempo Exh: "
        f"{r20['t_exhaustivo'] / r10['t_exhaustivo']:.2f}x | "
        f"Ops Exh: {r20['ops_exhaustivo'] / r10['ops_exhaustivo']:.2f}x"
    )
    print(
        f"d = 10.000 -> 20.000 | Tiempo PD: "
        f"{r20k['t_pd'] / r10k['t_pd']:.2f}x | "
        f"Ops PD: {r20k['ops_pd'] / r10k['ops_pd']:.2f}x"
    )
    print(
        f"d = 10.000 -> 20.000 | Tiempo Regla: "
        f"{r20k['t_regla'] / r10k['t_regla']:.2f}x | "
        f"Ops Regla: {r20k['ops_regla'] / r10k['ops_regla']:.2f}x"
    )

    # Extrapolación al volumen real: 950.000 tarjetas de d = 30 días
    r30 = mapa_gra[30]
    pendiente_pd = r20k["t_pd"] / 20000.0
    pendiente_reg = r20k["t_regla"] / 20000.0

    t_vol_pd = TARJETAS_VOLUMEN_REAL * r30["t_pd"]
    t_vol_reg = TARJETAS_VOLUMEN_REAL * r30["t_regla"]
    kwh_pd = POTENCIA_SERVIDOR_KW * (t_vol_pd / 3600.0)
    kwh_reg = POTENCIA_SERVIDOR_KW * (t_vol_reg / 3600.0)

    delta_m = r20["dias_activos"] - r10["dias_activos"]
    base_emp = (r20["t_exhaustivo"] / r10["t_exhaustivo"]) ** (1.0 / delta_m)
    m_30 = 27.0
    t_exh_1_tarjeta_30 = r20["t_exhaustivo"] * (
        base_emp ** (m_30 - r20["dias_activos"])
    )

    tarjetas_intensivas = int(0.15 * TARJETAS_VOLUMEN_REAL)
    t_vol_exh_intensivas_h = (
        tarjetas_intensivas * t_exh_1_tarjeta_30
    ) / 3600.0
    kwh_exh_intensivas = POTENCIA_SERVIDOR_KW * t_vol_exh_intensivas_h

    print("\n=== EXTRAPOLACIÓN AL VOLUMEN REAL (950.000 TARJETAS, d = 30) ===")
    print(
        f"Pendiente asintótica PD: {pendiente_pd * 1e6:.4f} µs/día | "
        f"t_PD(30) medido: {r30['t_pd'] * 1e6:.2f} µs/tarjeta"
    )
    print(
        f"Pendiente asintótica Regla: {pendiente_reg * 1e6:.4f} µs/día | "
        f"t_Regla(30) medido: {r30['t_regla'] * 1e6:.2f} µs/tarjeta"
    )
    print(
        f"PD (950.000 tarjetas): {t_vol_pd:.2f} s "
        f"({t_vol_pd / VENTANA_OPERATIVA_S * 100:.4f} % de ventana 4h) | "
        f"Energía: {kwh_pd:.6f} kWh/mes ({kwh_pd * 12:.5f} kWh/año)"
    )
    print(
        f"Regla actual sola (950.000 tarjetas): {t_vol_reg:.2f} s | "
        f"Energía: {kwh_reg:.6f} kWh/mes ({kwh_reg * 12:.5f} kWh/año)"
    )
    print(
        f"Exhaustivo base empírica r={base_emp:.3f}: 1 tarjeta (m=27) -> "
        f"{t_exh_1_tarjeta_30:.2f} s | 15% usuarios intensivos "
        f"({tarjetas_intensivas} tarjetas) -> "
        f"{t_vol_exh_intensivas_h:.1f} h | "
        f"Energía: {kwh_exh_intensivas:.1f} kWh/mes"
    )

    print("\n=== MEJORA ECONÓMICA EN MUESTRA SINTÉTICA (5.000 TARJETAS) ===")
    for dias_mes, info in mejora.items():
        print(
            f"Mes de {dias_mes} días: {info['porcentaje_afectadas']:.2f} % de "
            f"tarjetas sobrecobradas por la regla actual | "
            f"Promedio por afectada: ${info['promedio_por_afectada']:,.0f} | "
            f"Máximo: ${info['max_sobrecobro']:,.0f} | "
            f"Proyección 950k tarjetas: ${info['proyeccion_mensual_cop']:,.0f}"
        )


def ejecutar_experimentos() -> None:
    """Orquesta las mediciones, genera gráficas e imprime resultados."""
    raiz_repo = Path(__file__).resolve().parents[2]
    dir_graficas = raiz_repo / "graficas" / "tope_tarifario"

    pequenos = medir_tamanos_pequenos(semilla=SEMILLA_POR_DEFECTO)
    grandes = medir_tamanos_grandes(semilla=SEMILLA_POR_DEFECTO)
    mejora = medir_mejora_economica(semilla=SEMILLA_POR_DEFECTO)

    generar_grafica_tiempos(
        pequenos, grandes, dir_graficas / "tiempo_vs_n.png"
    )
    generar_grafica_operaciones(
        pequenos, grandes, dir_graficas / "operaciones_vs_n.png"
    )
    imprimir_resumen(pequenos, grandes, mejora)
    print(f"\nGráficas guardadas en: {dir_graficas}")


if __name__ == "__main__":
    ejecutar_experimentos()
