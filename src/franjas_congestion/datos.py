"""Generador de series sintéticas de saldos netos de plataforma (Operación 3)."""

import random

SEMILLA_POR_DEFECTO = 2026
INTERVALOS_POR_DIA = 228  # 04:30 a 23:30 en intervalos de 5 minutos


def generar_serie_estacion(
    intervalos: int,
    semilla: int = SEMILLA_POR_DEFECTO,
) -> list[int]:
    """Genera una serie sintética de saldos netos de pasajeros por intervalo.

    Simula el comportamiento horario de una estación del SITVM: horas pico de
    mañana y tarde con tendencia a acumulación positiva y horas valle con
    evacuación neta negativa.

    Args:
        intervalos: número total de intervalos de 5 minutos (n).
        semilla: semilla del generador pseudoaleatorio para reproducibilidad.

    Returns:
        Lista de enteros con el saldo neto (entradas menos salidas) en cada
        intervalo de 5 minutos.
    """
    rng = random.Random(semilla)
    serie: list[int] = []

    for idx in range(intervalos):
        pos_dia = idx % INTERVALOS_POR_DIA
        # Hora pico mañana (~06:00-08:30 -> intervalos 18..48)
        # Hora pico tarde (~16:30-19:30 -> intervalos 144..180)
        if 18 <= pos_dia <= 48 or 144 <= pos_dia <= 180:
            saldo = rng.randint(-35, 65)
        else:
            saldo = rng.randint(-60, 40)
        serie.append(saldo)

    return serie


def generar_lote_series(
    intervalos: int,
    cantidad: int = 10,
    semilla: int = SEMILLA_POR_DEFECTO,
) -> list[list[int]]:
    """Genera un lote de series sintéticas independientes del mismo tamaño n.

    Args:
        intervalos: longitud n de cada serie.
        cantidad: número de estaciones/series a generar en el lote.
        semilla: semilla base.

    Returns:
        Lista con `cantidad` series de longitud `intervalos`.
    """
    return [
        generar_serie_estacion(intervalos, semilla=semilla + i * 97 + intervalos)
        for i in range(cantidad)
    ]
