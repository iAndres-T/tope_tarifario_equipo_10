"""Regla simplificada actual para la liquidación del tope tarifario."""

PASAJE = 3900
DIARIO = 9500
SEMANAL = 36000
MENSUAL = 135000


def costo_regla_actual(viajes_por_dia: list[int]) -> int:
    """Calcula lo que cobra hoy la regla simplificada del sistema.

    Args:
        viajes_por_dia: viajes de la tarjeta en cada día del mes.

    Returns:
        El costo cobrado en pesos.
    """
    d = len(viajes_por_dia)
    if d == 0:
        return 0

    total = 0
    for inicio_mes in range(0, d, 30):
        fin_mes = min(inicio_mes + 30, d)
        suma_mes = 0

        for inicio_sem in range(inicio_mes, fin_mes, 7):
            fin_sem = min(inicio_sem + 7, fin_mes)
            suma_semana = 0

            for idx in range(inicio_sem, fin_sem):
                viajes_dia = viajes_por_dia[idx]
                if viajes_dia == 0:
                    continue
                sueltos = viajes_dia * PASAJE
                costo_dia = sueltos if sueltos < DIARIO else DIARIO
                suma_semana += costo_dia

            if suma_semana > SEMANAL:
                suma_semana = SEMANAL

            suma_mes += suma_semana
            if suma_mes > MENSUAL:
                suma_mes = MENSUAL

        total += suma_mes

    return total


def costo_regla_actual_conteo(viajes_por_dia: list[int]) -> tuple[int, int]:
    """Calcula el cobro de la regla actual y cuenta operaciones elementales.

    Args:
        viajes_por_dia: viajes de la tarjeta en cada día del periodo.

    Returns:
        Una tupla (costo_cobrado, operaciones) con el valor cobrado en pesos y
        el total de evaluaciones y comparaciones realizadas.
    """
    d = len(viajes_por_dia)
    if d == 0:
        return 0, 0

    total = 0
    operaciones = 0

    for inicio_mes in range(0, d, 30):
        fin_mes = min(inicio_mes + 30, d)
        suma_mes = 0

        for inicio_sem in range(inicio_mes, fin_mes, 7):
            fin_sem = min(inicio_sem + 7, fin_mes)
            suma_semana = 0

            for idx in range(inicio_sem, fin_sem):
                viajes_dia = viajes_por_dia[idx]
                if viajes_dia == 0:
                    operaciones += 1
                    continue
                sueltos = viajes_dia * PASAJE
                costo_dia = sueltos if sueltos < DIARIO else DIARIO
                suma_semana += costo_dia
                operaciones += 2

            operaciones += 1
            if suma_semana > SEMANAL:
                suma_semana = SEMANAL

            suma_mes += suma_semana
            operaciones += 1
            if suma_mes > MENSUAL:
                suma_mes = MENSUAL

        total += suma_mes

    return total, operaciones
