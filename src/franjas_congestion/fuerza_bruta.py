"""Detección de franjas de congestión mediante búsqueda exhaustiva (fuerza bruta)."""


def franja_fuerza_bruta(saldos: list[int]) -> tuple[int, int, int]:
    """Encuentra el tramo contiguo de mayor acumulación evaluando todos los pares.

    Reproduce el proceso actual del SITVM, que explora todos los tramos posibles
    (i, j) con 0 <= i <= j < n sobre la serie de saldos netos de plataforma.

    Args:
        saldos: serie de saldos netos de pasajeros por intervalo de 5 minutos
            (entradas por torniquetes menos evacuados por trenes). Contiene al
            menos un elemento.

    Returns:
        Una tupla (inicio, fin, acumulacion_maxima) con los índices inclusivos
        del tramo de mayor acumulación y el saldo neto acumulado en ese tramo.
        En caso de empate, conserva el primer tramo encontrado.
    """
    if not saldos:
        raise ValueError("La serie de saldos no puede estar vacía.")

    n = len(saldos)
    mejor_inicio = 0
    mejor_fin = 0
    mejor_suma = saldos[0]

    for i in range(n):
        acumulado = 0
        for j in range(i, n):
            acumulado += saldos[j]
            if acumulado > mejor_suma:
                mejor_suma = acumulado
                mejor_inicio = i
                mejor_fin = j

    return mejor_inicio, mejor_fin, mejor_suma


def franja_fuerza_bruta_conteo(
    saldos: list[int],
) -> tuple[tuple[int, int, int], int]:
    """Ejecuta fuerza bruta contando evaluaciones elementales de tramos.

    Args:
        saldos: serie de saldos netos de pasajeros por intervalo de 5 minutos.

    Returns:
        Tupla ((inicio, fin, acumulacion_maxima), operaciones) con el resultado
        exacto y el número de acumulaciones/comparaciones ejecutadas.
    """
    if not saldos:
        raise ValueError("La serie de saldos no puede estar vacía.")

    n = len(saldos)
    mejor_inicio = 0
    mejor_fin = 0
    mejor_suma = saldos[0]
    operaciones = 0

    for i in range(n):
        acumulado = 0
        for j in range(i, n):
            acumulado += saldos[j]
            operaciones += 1
            if acumulado > mejor_suma:
                mejor_suma = acumulado
                mejor_inicio = i
                mejor_fin = j

    return (mejor_inicio, mejor_fin, mejor_suma), operaciones
