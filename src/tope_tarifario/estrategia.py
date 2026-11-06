"""Liquidación del tope tarifario mediante programación dinámica."""

PASAJE = 3900
DIARIO = 9500
SEMANAL = 36000
MENSUAL = 135000

_DURACION_PRODUCTO: dict[str, int] = {
    "pasajes": 1,
    "diario": 1,
    "semanal": 7,
    "mensual": 30,
}


def costo_minimo(viajes_por_dia: list[int]) -> int:
    """Calcula el costo de la combinación más barata que cubre los viajes.

    Args:
        viajes_por_dia: viajes de la tarjeta en cada día del mes. El índice 0
            es el primer día; un día sin viajes vale 0.

    Returns:
        El costo mínimo en pesos.
    """
    d = len(viajes_por_dia)
    if d == 0:
        return 0

    costo: list[int] = [0] * (d + 2)
    for t in range(d, 0, -1):
        viajes_dia = viajes_por_dia[t - 1]
        if viajes_dia == 0:
            costo[t] = costo[t + 1]
            continue

        sueltos = viajes_dia * PASAJE
        costo_hoy = sueltos if sueltos < DIARIO else DIARIO
        mejor = costo_hoy + costo[t + 1]

        sig_semanal = t + 7 if t + 7 <= d + 1 else d + 1
        cand_semanal = SEMANAL + costo[sig_semanal]
        if cand_semanal < mejor:
            mejor = cand_semanal

        sig_mensual = t + 30 if t + 30 <= d + 1 else d + 1
        cand_mensual = MENSUAL + costo[sig_mensual]
        if cand_mensual < mejor:
            mejor = cand_mensual

        costo[t] = mejor

    return costo[1]


def liquidar_tope(viajes_por_dia: list[int], cobrado: int) -> int:
    """Calcula la devolución que corresponde al usuario.

    Args:
        viajes_por_dia: viajes de la tarjeta en cada día del mes.
        cobrado: pesos que se le cobraron durante el mes.

    Returns:
        La diferencia entre lo cobrado y el costo mínimo, nunca negativa.
    """
    diferencia = cobrado - costo_minimo(viajes_por_dia)
    return diferencia if diferencia > 0 else 0


def calcular_tabla_y_elecciones(
    viajes_por_dia: list[int],
) -> tuple[list[int], list[str]]:
    """Calcula la tabla completa de costos óptimos y la decisión de cada día.

    Args:
        viajes_por_dia: viajes de la tarjeta en cada día del periodo.

    Returns:
        Una tupla (costo, eleccion) indexada del día 1 al día d (con d + 1
        como caso base en cero), donde costo[t] es el mínimo desde el día t
        hasta el final y eleccion[t] indica el producto óptimo en el día t.
    """
    d = len(viajes_por_dia)
    costo: list[int] = [0] * (d + 2)
    eleccion: list[str] = ["nada"] * (d + 2)

    for t in range(d, 0, -1):
        viajes_dia = viajes_por_dia[t - 1]
        if viajes_dia == 0:
            costo[t] = costo[t + 1]
            continue

        sueltos = viajes_dia * PASAJE
        if sueltos < DIARIO:
            mejor = sueltos + costo[t + 1]
            mejor_opcion = "pasajes"
        else:
            mejor = DIARIO + costo[t + 1]
            mejor_opcion = "diario"

        sig_semanal = min(t + 7, d + 1)
        cand_semanal = SEMANAL + costo[sig_semanal]
        if cand_semanal < mejor:
            mejor = cand_semanal
            mejor_opcion = "semanal"

        sig_mensual = min(t + 30, d + 1)
        cand_mensual = MENSUAL + costo[sig_mensual]
        if cand_mensual < mejor:
            mejor = cand_mensual
            mejor_opcion = "mensual"

        costo[t] = mejor
        eleccion[t] = mejor_opcion

    return costo, eleccion


def reconstruir_compras(eleccion: list[str]) -> list[tuple[int, str]]:
    """Reconstruye la secuencia de productos comprados en una solución óptima.

    Args:
        eleccion: lista de decisiones por día devuelta por
            calcular_tabla_y_elecciones.

    Returns:
        Lista de tuplas (dia, producto) con las compras efectuadas, donde dia
        se numera desde 1.
    """
    d = len(eleccion) - 2
    compras: list[tuple[int, str]] = []
    t = 1
    while t <= d:
        producto = eleccion[t]
        if producto == "nada":
            t += 1
            continue
        compras.append((t, producto))
        t += _DURACION_PRODUCTO[producto]
    return compras


def costo_minimo_conteo(viajes_por_dia: list[int]) -> tuple[int, int]:
    """Calcula el costo mínimo contando las evaluaciones elementales de estado.

    Args:
        viajes_por_dia: viajes de la tarjeta en cada día del periodo.

    Returns:
        Una tupla (costo_optimo, operaciones) con el costo mínimo en pesos y el
        total de evaluaciones elementales realizadas en la tabla.
    """
    d = len(viajes_por_dia)
    if d == 0:
        return 0, 0

    costo: list[int] = [0] * (d + 2)
    operaciones = 0

    for t in range(d, 0, -1):
        viajes_dia = viajes_por_dia[t - 1]
        if viajes_dia == 0:
            costo[t] = costo[t + 1]
            operaciones += 1
            continue

        # Se evalúan las 4 opciones tarifarias disponibles para cubrir hoy
        mejor = viajes_dia * PASAJE + costo[t + 1]
        cand_diario = DIARIO + costo[t + 1]
        if cand_diario < mejor:
            mejor = cand_diario

        sig_semanal = t + 7 if t + 7 <= d + 1 else d + 1
        cand_semanal = SEMANAL + costo[sig_semanal]
        if cand_semanal < mejor:
            mejor = cand_semanal

        sig_mensual = t + 30 if t + 30 <= d + 1 else d + 1
        cand_mensual = MENSUAL + costo[sig_mensual]
        if cand_mensual < mejor:
            mejor = cand_mensual

        costo[t] = mejor
        operaciones += 4

    return costo[1], operaciones
