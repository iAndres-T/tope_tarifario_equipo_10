"""Suite de verificación con assert para la liquidación del tope tarifario."""

from pathlib import Path
import sys

_DIR_ACTUAL = Path(__file__).resolve().parent
if str(_DIR_ACTUAL) not in sys.path:
    sys.path.insert(0, str(_DIR_ACTUAL))

from datos import (
    SEMILLA_POR_DEFECTO,
    generar_instancias_pequenas,
)
from estrategia import (
    DIARIO,
    MENSUAL,
    PASAJE,
    SEMANAL,
    calcular_tabla_y_elecciones,
    costo_minimo,
    costo_minimo_conteo,
    liquidar_tope,
    reconstruir_compras,
)
from exhaustivo import (
    costo_exhaustivo,
    costo_exhaustivo_conteo,
)
from regla_actual import (
    costo_regla_actual,
    costo_regla_actual_conteo,
)


def evaluar_compras_reconstruidas(
    viajes_por_dia: list[int],
    compras: list[tuple[int, str]],
) -> tuple[int, bool]:
    """Recalcula independientemente el costo y cobertura de unas compras.

    Args:
        viajes_por_dia: serie de viajes diarios de la tarjeta.
        compras: lista de tuplas (dia, producto) devuelta por
            reconstruir_compras.

    Returns:
        Tupla (costo_total, cubre_todo) indicando el desembolso total y si
        todos los días con viajes quedaron debidamente cubiertos.
    """
    precios = {
        "diario": DIARIO,
        "semanal": SEMANAL,
        "mensual": MENSUAL,
    }
    duraciones = {
        "pasajes": 1,
        "diario": 1,
        "semanal": 7,
        "mensual": 30,
    }

    d = len(viajes_por_dia)
    cubierto = [False] * (d + 1)
    total = 0

    for dia_inicio, producto in compras:
        if producto == "pasajes":
            total += viajes_por_dia[dia_inicio - 1] * PASAJE
        else:
            total += precios[producto]

        fin = min(dia_inicio + duraciones[producto], d + 1)
        for t in range(dia_inicio, fin):
            cubierto[t] = True

    cubre_todo = all(
        cubierto[t] for t in range(1, d + 1) if viajes_por_dia[t - 1] > 0
    )
    return total, cubre_todo


def verificar_casos_limite() -> None:
    """Verifica entradas vacías, un día, cero viajes y demanda máxima."""
    # Entrada vacía
    assert costo_minimo([]) == 0
    assert costo_exhaustivo([]) == 0
    assert costo_regla_actual([]) == 0
    assert liquidar_tope([], 0) == 0

    # Un solo día con distintos conteos de viajes
    assert costo_minimo([0]) == 0
    assert costo_exhaustivo([0]) == 0
    assert costo_regla_actual([0]) == 0

    assert costo_minimo([1]) == PASAJE
    assert costo_exhaustivo([1]) == PASAJE
    assert costo_regla_actual([1]) == PASAJE

    assert costo_minimo([2]) == 2 * PASAJE
    assert costo_exhaustivo([2]) == 2 * PASAJE

    assert costo_minimo([3]) == DIARIO
    assert costo_exhaustivo([3]) == DIARIO
    assert costo_regla_actual([3]) == DIARIO

    assert costo_minimo([10]) == DIARIO
    assert costo_exhaustivo([10]) == DIARIO

    # Mes completo sin viajes
    assert costo_minimo([0] * 30) == 0
    assert costo_exhaustivo([0] * 30) == 0
    assert costo_regla_actual([0] * 30) == 0

    # Demanda intensiva: activa semanal, pase que sobra y mensual (30 y 31 d)
    assert costo_minimo([4] * 7) == SEMANAL
    assert costo_exhaustivo([4] * 7) == SEMANAL
    assert costo_regla_actual([4] * 7) == SEMANAL

    # Pase semanal que excede el periodo de 5 días (5 * 9500 = 47500 > 36000)
    assert costo_minimo([5] * 5) == SEMANAL
    assert costo_exhaustivo([5] * 5) == SEMANAL

    # Mes de 30 y 31 días con viajes intensivos diarios
    assert costo_minimo([4] * 30) == MENSUAL
    assert costo_regla_actual([4] * 30) == MENSUAL
    assert costo_minimo([4] * 31) == MENSUAL + DIARIO
    assert costo_minimo([1] + [4] * 30) == PASAJE + MENSUAL

    # Inmutabilidad de los datos originales de entrada
    original = [1, 3, 0, 2, 4]
    respaldo = list(original)
    _ = costo_minimo(original)
    _ = costo_exhaustivo(original)
    _ = costo_regla_actual(original)
    _ = liquidar_tope(original, 50000)
    assert original == respaldo


def verificar_ejemplo_parte_1() -> None:
    """Verifica paso a paso el ejemplo de 8 días resuelto a mano en Parte 1."""
    ejemplo = [1, 3, 2, 0, 3, 2, 3, 2]
    assert costo_minimo(ejemplo) == 39900
    assert costo_exhaustivo(ejemplo) == 39900

    tabla, elecciones = calcular_tabla_y_elecciones(ejemplo)
    esperada = [0, 39900, 36000, 36000, 34600, 34600, 25100, 17300, 7800, 0]
    assert tabla == esperada

    compras = reconstruir_compras(elecciones)
    assert compras == [(1, "pasajes"), (2, "semanal")]
    total_rec, cubre = evaluar_compras_reconstruidas(ejemplo, compras)
    assert cubre is True
    assert total_rec == 39900


def verificar_instancias_aleatorias(cantidad: int = 100) -> None:
    """Compara programación dinámica y exhaustiva en instancias aleatorias.

    Args:
        cantidad: número de instancias aleatorias con semilla fija (>= 20).
    """
    assert cantidad >= 20
    instancias = generar_instancias_pequenas(
        cantidad=cantidad,
        max_dias=14,
        semilla=SEMILLA_POR_DEFECTO,
    )

    for viajes in instancias:
        opt_pd = costo_minimo(viajes)
        opt_exh = costo_exhaustivo(viajes)
        cobro_regla = costo_regla_actual(viajes)

        assert opt_pd == opt_exh, f"Diferencia en instancia: {viajes}"
        assert cobro_regla >= opt_pd, f"Regla menor al óptimo en: {viajes}"

        tabla, elecciones = calcular_tabla_y_elecciones(viajes)
        assert tabla[1] == opt_pd, f"Tabla inconsistente en: {viajes}"
        compras = reconstruir_compras(elecciones)
        total_rec, cubre = evaluar_compras_reconstruidas(viajes, compras)
        assert cubre, f"Compras sin cubrir viajes en: {viajes}"
        assert total_rec == opt_pd, f"Costo reconstruido distinto en: {viajes}"

        c_pd_cnt, _ = costo_minimo_conteo(viajes)
        c_exh_cnt, _ = costo_exhaustivo_conteo(viajes)
        c_reg_cnt, _ = costo_regla_actual_conteo(viajes)
        assert c_pd_cnt == opt_pd
        assert c_exh_cnt == opt_exh
        assert c_reg_cnt == cobro_regla


def verificar_restriccion_negocio() -> None:
    """Verifica que la devolución sea exacta y nunca negativa."""
    viajes = [1, 3, 2, 0, 3, 2, 3, 2]
    minimo = costo_minimo(viajes)  # 39.900 pesos
    cobro_pasajes_sueltos = sum(v * PASAJE for v in viajes)  # 62.400 pesos

    devolucion = liquidar_tope(viajes, cobro_pasajes_sueltos)
    assert devolucion == cobro_pasajes_sueltos - minimo
    assert cobro_pasajes_sueltos - devolucion == minimo
    assert devolucion == 22500

    # Si se cobró exactamente el mínimo, la devolución es cero
    assert liquidar_tope(viajes, minimo) == 0

    # Si se cobró menos que el mínimo, nunca < 0
    assert liquidar_tope(viajes, minimo - 5000) == 0
    assert liquidar_tope(viajes, 0) == 0


def verificar_contraejemplo_regla_actual() -> None:
    """Verifica el contraejemplo calculado en Parte 1 contra regla_actual."""
    contraejemplo = [1, 1, 1, 3, 3, 3, 3, 3, 3, 3]
    cobro_actual = costo_regla_actual(contraejemplo)
    optimo = costo_minimo(contraejemplo)

    assert cobro_actual == 64500
    assert optimo == 47700
    assert costo_exhaustivo(contraejemplo) == 47700
    assert cobro_actual > optimo
    assert cobro_actual - optimo == 16800
    assert liquidar_tope(contraejemplo, cobro_actual) == 16800

    # El mismo contraejemplo extendido a un mes calendario de 30 días
    contraejemplo_mes = contraejemplo + [0] * 20
    assert costo_regla_actual(contraejemplo_mes) == 64500
    assert costo_minimo(contraejemplo_mes) == 47700

    # Contraejemplo adicional en mes de 31 dias
    mes_31 = [1] + [4] * 30
    assert costo_regla_actual(mes_31) == 144500
    assert costo_minimo(mes_31) == 138900
    assert costo_regla_actual(mes_31) - costo_minimo(mes_31) == 5600


def test_suite_completa() -> None:
    """Punto de entrada compatible con pytest."""
    ejecutar_pruebas()


def ejecutar_pruebas() -> None:
    """Ejecuta todas las verificaciones con assert del Caso 1."""
    verificar_casos_limite()
    verificar_ejemplo_parte_1()
    verificar_instancias_aleatorias(cantidad=100)
    verificar_restriccion_negocio()
    verificar_contraejemplo_regla_actual()


if __name__ == "__main__":
    ejecutar_pruebas()
    print(
        "Verificación exitosa: casos límite, ejemplo manual, 100 instancias "
        "aleatorias, restricción del negocio y contraejemplo superados."
    )
