from config.choices import TipoSeleccionMercado


SELECTION_ORDER = {
    TipoSeleccionMercado.LOCAL: 10,
    TipoSeleccionMercado.EMPATE: 20,
    TipoSeleccionMercado.VISITANTE: 30,
    TipoSeleccionMercado.LOCAL_EMPATE: 40,
    TipoSeleccionMercado.LOCAL_VISITANTE: 50,
    TipoSeleccionMercado.EMPATE_VISITANTE: 60,
    TipoSeleccionMercado.OVER_05: 70,
    TipoSeleccionMercado.UNDER_05: 80,
    TipoSeleccionMercado.OVER_15: 90,
    TipoSeleccionMercado.UNDER_15: 100,
    TipoSeleccionMercado.OVER_25: 110,
    TipoSeleccionMercado.UNDER_25: 120,
    TipoSeleccionMercado.OVER_35: 130,
    TipoSeleccionMercado.UNDER_35: 140,
    TipoSeleccionMercado.AMBOS_SI: 150,
    TipoSeleccionMercado.AMBOS_NO: 160,
    TipoSeleccionMercado.EXACT_0: 170,
    TipoSeleccionMercado.EXACT_1: 180,
    TipoSeleccionMercado.EXACT_2: 190,
    TipoSeleccionMercado.EXACT_3: 200,
    TipoSeleccionMercado.EXACT_4_PLUS: 210,
}


def ordered_selections(selecciones):
    return sorted(
        selecciones,
        key=lambda seleccion: SELECTION_ORDER.get(seleccion.tipo, 999),
    )
