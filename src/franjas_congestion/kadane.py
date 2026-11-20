"""Detección de franjas de congestión mediante programación dinámica lineal (Kadane)."""


def franja_programacion_dinamica(saldos: list[int]) -> tuple[int, int, int]:
    """Encuentra el tramo contiguo de mayor acumulación en tiempo lineal Theta(n).

    Define el estado M(j) como la mayor acumulación de un tramo contiguo que
    termina exactamente en el intervalo j:
        M(j) = max(saldos[j], M(j - 1) + saldos[j])
    Como M(j) solo depende de M(j - 1), mantiene el estado en O(1) memoria.

    Args:
        saldos: serie de saldos netos de pasajeros por intervalo de 5 minutos.

    Returns:
        Tupla (inicio, fin, acumulacion_maxima) del tramo de mayor acumulación.
    """
    if not saldos:
        raise ValueError("La serie de saldos no puede estar vacía.")

    mejor_inicio = 0
    mejor_fin = 0
    mejor_suma = saldos[0]

    inicio_actual = 0
    suma_actual = saldos[0]

    for j in range(1, len(saldos)):
        valor = saldos[j]
        if suma_actual + valor >= valor:
            suma_actual += valor
        else:
            suma_actual = valor
            inicio_actual = j

        if suma_actual > mejor_suma:
            mejor_suma = suma_actual
            mejor_inicio = inicio_actual
            mejor_fin = j

    return mejor_inicio, mejor_fin, mejor_suma


def franja_programacion_dinamica_conteo(
    saldos: list[int],
) -> tuple[tuple[int, int, int], int]:
    """Ejecuta el algoritmo lineal de Kadane contando operaciones elementales.

    Args:
        saldos: serie de saldos netos de pasajeros por intervalo de 5 minutos.

    Returns:
        Tupla ((inicio, fin, acumulacion_maxima), operaciones).
    """
    if not saldos:
        raise ValueError("La serie de saldos no puede estar vacía.")

    mejor_inicio = 0
    mejor_fin = 0
    mejor_suma = saldos[0]

    inicio_actual = 0
    suma_actual = saldos[0]
    operaciones = 1

    for j in range(1, len(saldos)):
        valor = saldos[j]
        operaciones += 1
        if suma_actual + valor >= valor:
            suma_actual += valor
        else:
            suma_actual = valor
            inicio_actual = j

        if suma_actual > mejor_suma:
            mejor_suma = suma_actual
            mejor_inicio = inicio_actual
            mejor_fin = j

    return (mejor_inicio, mejor_fin, mejor_suma), operaciones
