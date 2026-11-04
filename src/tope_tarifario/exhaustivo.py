"""Solución exhaustiva para la liquidación del tope tarifario."""

PASAJE = 3900
DIARIO = 9500
SEMANAL = 36000
MENSUAL = 135000


def _explorar_combinaciones(viajes_por_dia: list[int], indice: int) -> int:
    """Explora recursivamente todas las combinaciones desde un día dado.

    Args:
        viajes_por_dia: viajes de la tarjeta en cada día del periodo.
        indice: posición actual (basada en 0) pendiente por cubrir.

    Returns:
        El costo mínimo en pesos para cubrir desde indice hasta el final.
    """
    if indice >= len(viajes_por_dia):
        return 0

    viajes_dia = viajes_por_dia[indice]
    if viajes_dia == 0:
        return _explorar_combinaciones(viajes_por_dia, indice + 1)

    op_pasajes = viajes_dia * PASAJE + _explorar_combinaciones(
        viajes_por_dia, indice + 1
    )
    op_diario = DIARIO + _explorar_combinaciones(viajes_por_dia, indice + 1)
    op_semanal = SEMANAL + _explorar_combinaciones(viajes_por_dia, indice + 7)
    op_mensual = MENSUAL + _explorar_combinaciones(viajes_por_dia, indice + 30)

    mejor = op_pasajes
    if op_diario < mejor:
        mejor = op_diario
    if op_semanal < mejor:
        mejor = op_semanal
    if op_mensual < mejor:
        mejor = op_mensual
    return mejor


def costo_exhaustivo(viajes_por_dia: list[int]) -> int:
    """Calcula el mismo costo probando todas las combinaciones de productos.

    Args:
        viajes_por_dia: viajes de la tarjeta en cada día del mes.

    Returns:
        El costo mínimo en pesos.
    """
    return _explorar_combinaciones(viajes_por_dia, 0)


def _explorar_con_conteo(
    viajes_por_dia: list[int], indice: int
) -> tuple[int, int]:
    """Explora todas las combinaciones contando evaluaciones elementales.

    Args:
        viajes_por_dia: viajes de la tarjeta en cada día del periodo.
        indice: posición actual (basada en 0) pendiente por cubrir.

    Returns:
        Tupla (costo_minimo, operaciones) acumulada en el subárbol recursivo.
    """
    if indice >= len(viajes_por_dia):
        return 0, 0

    viajes_dia = viajes_por_dia[indice]
    if viajes_dia == 0:
        sub_costo, sub_ops = _explorar_con_conteo(viajes_por_dia, indice + 1)
        return sub_costo, sub_ops + 1

    c_pas, o_pas = _explorar_con_conteo(viajes_por_dia, indice + 1)
    op_pasajes = viajes_dia * PASAJE + c_pas

    c_dia, o_dia = _explorar_con_conteo(viajes_por_dia, indice + 1)
    op_diario = DIARIO + c_dia

    c_sem, o_sem = _explorar_con_conteo(viajes_por_dia, indice + 7)
    op_semanal = SEMANAL + c_sem

    c_men, o_men = _explorar_con_conteo(viajes_por_dia, indice + 30)
    op_mensual = MENSUAL + c_men

    mejor = op_pasajes
    if op_diario < mejor:
        mejor = op_diario
    if op_semanal < mejor:
        mejor = op_semanal
    if op_mensual < mejor:
        mejor = op_mensual

    operaciones = 4 + o_pas + o_dia + o_sem + o_men
    return mejor, operaciones


def costo_exhaustivo_conteo(viajes_por_dia: list[int]) -> tuple[int, int]:
    """Calcula el costo exhaustivo y el número de evaluaciones exploradas.

    Args:
        viajes_por_dia: viajes de la tarjeta en cada día del periodo.

    Returns:
        Una tupla (costo_optimo, operaciones) con el costo mínimo en pesos y el
        total de evaluaciones realizadas en el árbol recursivo.
    """
    return _explorar_con_conteo(viajes_por_dia, 0)
