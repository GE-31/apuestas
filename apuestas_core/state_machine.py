from config.choices import EstadoApuesta

class TransicionEstadoApuestaError(Exception):
    pass

TRANSICIONES_PERMITIDAS = {
    EstadoApuesta.BORRADOR: [
        EstadoApuesta.ACCEPTED,
        EstadoApuesta.CANCELLED,
    ],
    EstadoApuesta.ACCEPTED: [
        EstadoApuesta.WON,
        EstadoApuesta.LOST,
        EstadoApuesta.CANCELLED,
        EstadoApuesta.CASHED_OUT,
        EstadoApuesta.VOID,
    ],
    EstadoApuesta.WON: [],
    EstadoApuesta.LOST: [],
    EstadoApuesta.CANCELLED: [],
    EstadoApuesta.CASHED_OUT: [],
    EstadoApuesta.VOID: [],
}


def puede_transicionar(estado_actual, nuevo_estado):
    """
    Verifica si una apuesta puede cambiar de un estado a otro.
    """

    estados_permitidos = TRANSICIONES_PERMITIDAS.get(estado_actual, [])
    return nuevo_estado in estados_permitidos


def validar_transicion_estado(estado_actual, nuevo_estado):
    """
    Lanza error si la transición no está permitida.
    """

    if not puede_transicionar(estado_actual, nuevo_estado):
        raise TransicionEstadoApuestaError(
            f'No se puede cambiar la apuesta de {estado_actual} a {nuevo_estado}.'
        )

    return True


def cambiar_estado_apuesta(bet, nuevo_estado, guardar=True):
    """
    Cambia el estado de una apuesta validando la máquina de estados.

    Nota:
    - Aquí solo se valida el cambio de estado.
    - La lógica de liquidación, pago o cash-out va en services/.
    """

    validar_transicion_estado(bet.estado, nuevo_estado)

    bet.estado = nuevo_estado

    if guardar:
        bet.save(update_fields=['estado', 'fecha_actualizacion'])

    return bet


def es_estado_final(estado):
    """
    Indica si una apuesta ya terminó su ciclo de vida.
    """

    return estado in [
        EstadoApuesta.WON,
        EstadoApuesta.LOST,
        EstadoApuesta.CANCELLED,
        EstadoApuesta.CASHED_OUT,
        EstadoApuesta.VOID,
    ]


def apuesta_esta_activa(bet):
    """
    Una apuesta activa es una apuesta aceptada y pendiente de liquidación.
    """

    return bet.estado == EstadoApuesta.ACCEPTED