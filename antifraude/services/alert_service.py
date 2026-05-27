from antifraude.models import FraudAlert


def crear_alerta_antifraude(
    *,
    usuario,
    tipo_alerta,
    severidad,
    descripcion,
    bet=None,
    metadata=None,
):
    """
    Persiste una FraudAlert.
    No lanza excepciones al caller — el fraude nunca bloquea la apuesta.
    """
    return FraudAlert.objects.create(
        usuario=usuario,
        bet=bet,
        tipo_alerta=tipo_alerta,
        severidad=severidad,
        descripcion=descripcion,
        metadata=metadata or {},
    )
