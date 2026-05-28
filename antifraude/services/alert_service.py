from antifraude.models import FraudAlert
from auditoria.services.audit_service import auditar_alerta_antifraude


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
    alerta = FraudAlert.objects.create(
        usuario=usuario,
        bet=bet,
        tipo_alerta=tipo_alerta,
        severidad=severidad,
        descripcion=descripcion,
        metadata=metadata or {},
    )

    auditar_alerta_antifraude(
        entidad="FraudAlert",
        entidad_id=alerta.id,
        accion="created",
        payload={
            "usuario_id": usuario.id,
            "bet_id": bet.id if bet else None,
            "tipo_alerta": alerta.tipo_alerta,
            "severidad": alerta.severidad,
            "estado": alerta.estado,
            "descripcion": alerta.descripcion,
            "metadata": alerta.metadata,
        },
    )

    return alerta
