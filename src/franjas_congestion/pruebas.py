"""Suite de verificación con assert para la Operación 3: franjas de congestión."""

from pathlib import Path
import random
import sys

_DIR_ACTUAL = Path(__file__).resolve().parent
if str(_DIR_ACTUAL) not in sys.path:
    sys.path.insert(0, str(_DIR_ACTUAL))

from datos import generar_serie_estacion
from divide_y_venceras import (
    franja_divide_y_venceras,
    franja_divide_y_venceras_conteo,
)
from fuerza_bruta import franja_fuerza_bruta, franja_fuerza_bruta_conteo
from kadane import (
    franja_programacion_dinamica,
    franja_programacion_dinamica_conteo,
)


def verificar_traza_manual() -> None:
    """Verifica el ejemplo de 8 intervalos resuelto a mano en el informe."""
    # Serie de 8 intervalos de 5 minutos (40 minutos en hora pico)
    serie = [-15, 40, -10, 35, -50, 20, 45, -25]
    copia = list(serie)

    res_fb = franja_fuerza_bruta(serie)
    res_dyv = franja_divide_y_venceras(serie)
    res_pd = franja_programacion_dinamica(serie)

    # El mejor tramo va del índice 1 al 6: 40 - 10 + 35 - 50 + 20 + 45 = 80
    assert res_fb == (1, 6, 80), f"Fallo FB en traza manual: {res_fb}"
    assert res_dyv == (1, 6, 80), f"Fallo DyV en traza manual: {res_dyv}"
    assert res_pd == (1, 6, 80), f"Fallo PD en traza manual: {res_pd}"
    assert serie == copia, "La lista original fue modificada."


def verificar_casos_borde() -> None:
    """Verifica series de un elemento, todas negativas, todas positivas y cruces."""
    # 1. Un solo intervalo (positivo y negativo)
    assert franja_fuerza_bruta([25]) == (0, 0, 25)
    assert franja_divide_y_venceras([25]) == (0, 0, 25)
    assert franja_programacion_dinamica([25]) == (0, 0, 25)

    assert franja_fuerza_bruta([-12]) == (0, 0, -12)
    assert franja_divide_y_venceras([-12]) == (0, 0, -12)
    assert franja_programacion_dinamica([-12]) == (0, 0, -12)

    # 2. Todos los saldos negativos (gana el intervalo menos negativo)
    todos_neg = [-40, -15, -30, -5, -22]
    assert franja_fuerza_bruta(todos_neg)[2] == -5
    assert franja_divide_y_venceras(todos_neg)[2] == -5
    assert franja_programacion_dinamica(todos_neg)[2] == -5

    # 3. Todos los saldos positivos (gana toda la serie completa)
    todos_pos = [10, 20, 15, 30, 5]
    assert franja_fuerza_bruta(todos_pos) == (0, 4, 80)
    assert franja_divide_y_venceras(todos_pos) == (0, 4, 80)
    assert franja_programacion_dinamica(todos_pos) == (0, 4, 80)

    # 4. Caso donde el mejor tramo cruza exactamente la mitad
    cruzado = [-50, -40, 30, 45, 50, 25, -60, -30]
    assert franja_fuerza_bruta(cruzado) == (2, 5, 150)
    assert franja_divide_y_venceras(cruzado) == (2, 5, 150)
    assert franja_programacion_dinamica(cruzado) == (2, 5, 150)


def verificar_instancias_aleatorias() -> None:
    """Verifica 100 series aleatorias comparando las tres estrategias y sus conteos."""
    rng = random.Random(2026)
    for idx in range(100):
        n = rng.randint(1, 120)
        serie = generar_serie_estacion(n, semilla=2026 + idx)
        copia = list(serie)

        res_fb = franja_fuerza_bruta(serie)
        res_dyv = franja_divide_y_venceras(serie)
        res_pd = franja_programacion_dinamica(serie)

        # Inmutabilidad
        assert serie == copia, "Se alteró la serie de entrada."

        # Exactitud de la acumulación máxima entre las 3 estrategias
        assert res_fb[2] == res_dyv[2] == res_pd[2], (
            f"Discrepancia en suma máxima (instancia {idx}): "
            f"FB={res_fb}, DyV={res_dyv}, PD={res_pd}"
        )

        # Verificar que los índices devueltos por cada una realmente suman ese máximo
        assert sum(serie[res_fb[0] : res_fb[1] + 1]) == res_fb[2]
        assert sum(serie[res_dyv[0] : res_dyv[1] + 1]) == res_dyv[2]
        assert sum(serie[res_pd[0] : res_pd[1] + 1]) == res_pd[2]

        # Verificar que las funciones gemelas de conteo devuelven el mismo máximo
        (c_fb, ops_fb) = franja_fuerza_bruta_conteo(serie)
        (c_dyv, ops_dyv) = franja_divide_y_venceras_conteo(serie)
        (c_pd, ops_pd) = franja_programacion_dinamica_conteo(serie)
        assert c_fb[2] == res_fb[2] and ops_fb == n * (n + 1) // 2
        assert c_dyv[2] == res_dyv[2] and ops_dyv >= n
        assert c_pd[2] == res_pd[2] and ops_pd == n


def ejecutar_pruebas() -> None:
    """Ejecuta toda la batería de pruebas de la Operación 3."""
    verificar_traza_manual()
    verificar_casos_borde()
    verificar_instancias_aleatorias()
    print(
        "OK: Todas las pruebas de franjas de congestión (fuerza bruta, "
        "dividir y vencer y programación dinámica) pasaron correctamente."
    )


if __name__ == "__main__":
    ejecutar_pruebas()
