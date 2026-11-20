"""Detección de franjas de congestión mediante dividir y vencer."""


def _franja_cruzada(
    saldos: list[int], inicio: int, medio: int, fin: int
) -> tuple[int, int, int]:
    """Encuentra el mejor tramo contiguo que cruza la frontera entre medio y medio + 1.

    Args:
        saldos: serie de saldos netos de pasajeros por intervalo.
        inicio: índice inicial del subarreglo actual (inclusivo).
        medio: índice de corte de la mitad izquierda (inclusivo).
        fin: índice final del subarreglo actual (inclusivo).

    Returns:
        Tupla (indice_izq, indice_der, suma_cruzada) del tramo de mayor
        acumulación que contiene al menos los índices medio y medio + 1.
    """
    suma_izq = 0
    mejor_izq = saldos[medio]
    idx_izq = medio
    for i in range(medio, inicio - 1, -1):
        suma_izq += saldos[i]
        if suma_izq >= mejor_izq:
            mejor_izq = suma_izq
            idx_izq = i

    suma_der = 0
    mejor_der = saldos[medio + 1]
    idx_der = medio + 1
    for j in range(medio + 1, fin + 1):
        suma_der += saldos[j]
        if suma_der > mejor_der:
            mejor_der = suma_der
            idx_der = j

    return idx_izq, idx_der, mejor_izq + mejor_der


def _resolver_dyv(
    saldos: list[int], inicio: int, fin: int
) -> tuple[int, int, int]:
    """Resuelve recursivamente el subarreglo máximo en saldos[inicio..fin].

    Args:
        saldos: serie de saldos netos de pasajeros.
        inicio: límite izquierdo inclusivo.
        fin: límite derecho inclusivo.

    Returns:
        Tupla (mejor_inicio, mejor_fin, mejor_suma) dentro del rango dado.
    """
    if inicio == fin:
        return inicio, fin, saldos[inicio]

    medio = (inicio + fin) // 2
    izq = _resolver_dyv(saldos, inicio, medio)
    der = _resolver_dyv(saldos, medio + 1, fin)
    cruz = _franja_cruzada(saldos, inicio, medio, fin)

    if izq[2] >= der[2] and izq[2] >= cruz[2]:
        return izq
    if cruz[2] >= izq[2] and cruz[2] >= der[2]:
        return cruz
    return der


def franja_divide_y_venceras(saldos: list[int]) -> tuple[int, int, int]:
    """Encuentra el tramo contiguo de mayor acumulación por dividir y vencer.

    Divide la serie en dos mitades iguales, resuelve recursivamente cada mitad
    y combina en tiempo lineal evaluando el mejor tramo que cruza el centro:
    T(n) = 2T(n/2) + Theta(n) => Theta(n log n).

    Args:
        saldos: serie de saldos netos de pasajeros por intervalo de 5 minutos.

    Returns:
        Tupla (inicio, fin, acumulacion_maxima) del tramo óptimo.
    """
    if not saldos:
        raise ValueError("La serie de saldos no puede estar vacía.")
    return _resolver_dyv(saldos, 0, len(saldos) - 1)


def _resolver_dyv_conteo(
    saldos: list[int], inicio: int, fin: int
) -> tuple[tuple[int, int, int], int]:
    """Resuelve por dividir y vencer contando operaciones elementales.

    Args:
        saldos: serie de saldos netos de pasajeros.
        inicio: límite izquierdo inclusivo.
        fin: límite derecho inclusivo.

    Returns:
        Tupla ((mejor_inicio, mejor_fin, mejor_suma), operaciones).
    """
    if inicio == fin:
        return (inicio, fin, saldos[inicio]), 1

    medio = (inicio + fin) // 2
    izq, ops_izq = _resolver_dyv_conteo(saldos, inicio, medio)
    der, ops_der = _resolver_dyv_conteo(saldos, medio + 1, fin)

    # Barrido cruzado contando cada paso del barrido izquierdo y derecho
    suma_izq = 0
    mejor_izq = saldos[medio]
    idx_izq = medio
    ops_cruz = 0
    for i in range(medio, inicio - 1, -1):
        suma_izq += saldos[i]
        ops_cruz += 1
        if suma_izq >= mejor_izq:
            mejor_izq = suma_izq
            idx_izq = i

    suma_der = 0
    mejor_der = saldos[medio + 1]
    idx_der = medio + 1
    for j in range(medio + 1, fin + 1):
        suma_der += saldos[j]
        ops_cruz += 1
        if suma_der > mejor_der:
            mejor_der = suma_der
            idx_der = j

    cruz = (idx_izq, idx_der, mejor_izq + mejor_der)
    total_ops = ops_izq + ops_der + ops_cruz

    if izq[2] >= der[2] and izq[2] >= cruz[2]:
        return izq, total_ops
    if cruz[2] >= izq[2] and cruz[2] >= der[2]:
        return cruz, total_ops
    return der, total_ops


def franja_divide_y_venceras_conteo(
    saldos: list[int],
) -> tuple[tuple[int, int, int], int]:
    """Ejecuta dividir y vencer contando operaciones elementales.

    Args:
        saldos: serie de saldos netos de pasajeros por intervalo de 5 minutos.

    Returns:
        Tupla ((inicio, fin, acumulacion_maxima), operaciones).
    """
    if not saldos:
        raise ValueError("La serie de saldos no puede estar vacía.")
    return _resolver_dyv_conteo(saldos, 0, len(saldos) - 1)
