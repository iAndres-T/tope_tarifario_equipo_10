"""Generador de instancias sintéticas reproducibles para el tope tarifario."""

import random

SEMILLA_POR_DEFECTO = 2026
_PERFIL_VIAJES_ACTIVO: tuple[int, ...] = (1, 2, 2, 3, 3, 4, 5)


def generar_viajes_periodo(
    dias: int,
    rng: random.Random,
    prob_viaje: float = 0.9,
) -> list[int]:
    """Genera la serie diaria de viajes de una tarjeta frecuente.

    Args:
        dias: cantidad de días d del periodo a simular.
        rng: generador pseudoaleatorio ya inicializado con semilla fija.
        prob_viaje: probabilidad de que un día tenga al menos un viaje.

    Returns:
        Lista de longitud dias con el número de viajes de cada día.
    """
    viajes: list[int] = []
    for _ in range(dias):
        if rng.random() < prob_viaje:
            viajes.append(rng.choice(_PERFIL_VIAJES_ACTIVO))
        else:
            viajes.append(0)
    return viajes


def generar_lote_experimento(
    dias: int,
    cantidad: int = 15,
    semilla: int = SEMILLA_POR_DEFECTO,
    prob_viaje: float = 0.9,
) -> list[list[int]]:
    """Genera un lote reproducible de instancias para un tamaño d dado.

    Args:
        dias: número de días d de cada instancia del lote.
        cantidad: número de instancias a generar para promediar mediciones.
        semilla: semilla base para garantizar reproducibilidad exacta.
        prob_viaje: fracción esperada de días con viajes en el periodo.

    Returns:
        Lista con cantidad instancias, cada una de longitud dias.
    """
    rng = random.Random(semilla + dias * 1009)
    return [
        generar_viajes_periodo(dias, rng, prob_viaje=prob_viaje)
        for _ in range(cantidad)
    ]


def generar_instancias_pequenas(
    cantidad: int = 100,
    max_dias: int = 14,
    semilla: int = SEMILLA_POR_DEFECTO,
) -> list[list[int]]:
    """Genera instancias pequeñas variadas para verificación con exhaustivo.

    Args:
        cantidad: número de instancias aleatorias a construir.
        max_dias: cota superior de días del periodo para mantener tratable
            la búsqueda exhaustiva.
        semilla: semilla fija de reproducibilidad.

    Returns:
        Lista de series de viajes por día con densidades diversas.
    """
    rng = random.Random(semilla)
    instancias: list[list[int]] = []
    for _ in range(cantidad):
        d = rng.randint(0, max_dias)
        prob = rng.uniform(0.2, 1.0)
        viajes = [
            rng.randint(1, 6) if rng.random() < prob else 0 for _ in range(d)
        ]
        instancias.append(viajes)
    return instancias


def generar_muestra_usuarios_mes(
    cantidad: int = 5000,
    dias_mes: int = 30,
    semilla: int = SEMILLA_POR_DEFECTO,
) -> list[list[int]]:
    """Genera una muestra sintética de tarjetas activas en un mes del SITVM.

    Modela cuatro perfiles de uso mensual: ocasional (25 %), intermitente o
    turnos variables (35 %), laboral de lunes a sábado (25 %) e intensivo
    diario (15 %).

    Args:
        cantidad: número de tarjetas activas a simular.
        dias_mes: duración del mes calendario (28, 30 o 31 días).
        semilla: semilla fija para reproducibilidad.

    Returns:
        Lista de tarjetas, cada una representada por sus viajes por día.
    """
    rng = random.Random(semilla + dias_mes * 313)
    tarjetas: list[list[int]] = []

    for _ in range(cantidad):
        perfil = rng.random()
        if perfil < 0.25:
            # Usuario ocasional: pocos días al mes, 1 a 3 viajes
            viajes = [
                rng.randint(1, 3) if rng.random() < 0.20 else 0
                for _ in range(dias_mes)
            ]
        elif perfil < 0.60:
            # Usuario intermitente o por rachas laborales desplazadas
            inicio_racha = rng.randint(0, max(0, dias_mes - 10))
            largo_racha = rng.randint(6, 12)
            viajes = []
            for dia in range(dias_mes):
                if inicio_racha <= dia < inicio_racha + largo_racha:
                    viajes.append(rng.randint(2, 4))
                elif rng.random() < 0.20:
                    viajes.append(rng.randint(1, 2))
                else:
                    viajes.append(0)
        elif perfil < 0.85:
            # Usuario frecuente: viaja 75 % de los días, 2 a 4 viajes
            viajes = [
                rng.randint(2, 4) if rng.random() < 0.75 else 0
                for _ in range(dias_mes)
            ]
        else:
            # Usuario intensivo: viaja 92 % de los días, 3 a 5 viajes
            viajes = [
                rng.randint(3, 5) if rng.random() < 0.92 else 0
                for _ in range(dias_mes)
            ]

        if sum(viajes) == 0 and dias_mes > 0:
            viajes[rng.randint(0, dias_mes - 1)] = 1
        tarjetas.append(viajes)

    return tarjetas
