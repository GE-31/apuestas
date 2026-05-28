from auditoria.models import AuditIntegrityCheck, AuditLog
from auditoria.services.hash_chain_service import (
    crear_registro_auditoria,
    verificar_integridad_cadena,
)


def auditar_movimiento_wallet(
    *,
    transaction,
    creado_por=None,
    ip_origen=None,
    user_agent=None,
):
    """
    Registra en auditoría una transacción de billetera.
    Ejemplo: recarga, retiro, bloqueo de apuesta, liquidación.
    """

    entries = []

    for entry in transaction.entries.all():
        entries.append({
            "account_id": entry.account_id,
            "account_nombre": entry.account.nombre,
            "amount": str(entry.amount),
            "direction": entry.direction,
            "descripcion": entry.descripcion,
        })

    payload = {
        "transaction_id": transaction.id,
        "tipo": transaction.tipo,
        "referencia": transaction.referencia,
        "idempotency_key": transaction.idempotency_key,
        "descripcion": transaction.descripcion,
        "entries": entries,
        "fecha_creacion": str(transaction.fecha_creacion),
    }

    return crear_registro_auditoria(
        tipo_evento=AuditLog.TipoEvento.WALLET_MOVEMENT,
        entidad="LedgerTransaction",
        entidad_id=transaction.id,
        accion="created",
        payload=payload,
        creado_por=creado_por,
        ip_origen=ip_origen,
        user_agent=user_agent,
    )


def auditar_apuesta_creada(
    *,
    bet,
    creado_por=None,
    ip_origen=None,
    user_agent=None,
):
    """
    Registra en auditoría una apuesta creada.
    """

    selecciones = []

    for seleccion in bet.selecciones.all():
        selecciones.append({
            "seleccion_id": seleccion.seleccion_id,
            "seleccion_nombre": seleccion.seleccion.nombre,
            "odd_id": seleccion.odd_id,
            "odd_valor_tomado": str(seleccion.odd_valor_tomado),
            "resultado": seleccion.resultado,
        })

    payload = {
        "bet_id": bet.id,
        "usuario_id": bet.usuario_id,
        "tipo": bet.tipo,
        "estado": bet.estado,
        "stake": str(bet.stake),
        "odds_total": str(bet.odds_total),
        "payout_potencial": str(bet.payout_potencial),
        "idempotency_key": bet.idempotency_key,
        "ip_origen": bet.ip_origen,
        "aceptada_en": str(bet.aceptada_en),
        "selecciones": selecciones,
    }

    return crear_registro_auditoria(
        tipo_evento=AuditLog.TipoEvento.BET_CREATED,
        entidad="Bet",
        entidad_id=bet.id,
        accion="created",
        payload=payload,
        creado_por=creado_por,
        ip_origen=ip_origen,
        user_agent=user_agent,
    )


def auditar_apuesta_liquidada(
    *,
    bet,
    accion,
    creado_por=None,
    ip_origen=None,
    user_agent=None,
):
    """
    Registra en auditoría una apuesta liquidada.

    accion puede ser:
    - won
    - lost
    - void
    - cashed_out
    """

    payload = {
        "bet_id": bet.id,
        "usuario_id": bet.usuario_id,
        "estado": bet.estado,
        "stake": str(bet.stake),
        "odds_total": str(bet.odds_total),
        "payout_potencial": str(bet.payout_potencial),
        "payout_final": str(bet.payout_final),
        "liquidada_en": str(bet.liquidada_en),
    }

    return crear_registro_auditoria(
        tipo_evento=AuditLog.TipoEvento.BET_SETTLED,
        entidad="Bet",
        entidad_id=bet.id,
        accion=accion,
        payload=payload,
        creado_por=creado_por,
        ip_origen=ip_origen,
        user_agent=user_agent,
    )


def auditar_kyc(
    *,
    perfil,
    kyc,
    accion,
    creado_por=None,
    ip_origen=None,
    user_agent=None,
):
    """
    Registra cambios del KYC simulado y estado de cuenta del usuario.
    """

    payload = {
        "perfil_id": perfil.id,
        "usuario_id": perfil.usuario_id,
        "estado_cuenta": perfil.estado_cuenta,
        "dni_verificado": kyc.dni_verificado,
        "mayor_edad_verificado": kyc.mayor_edad_verificado,
        "fecha_verificacion": str(kyc.fecha_verificacion),
        "observacion": kyc.observacion,
        "verificado_por_id": kyc.verificado_por_id,
    }

    return crear_registro_auditoria(
        tipo_evento=AuditLog.TipoEvento.USER_KYC,
        entidad="VerificacionKYC",
        entidad_id=kyc.id,
        accion=accion,
        payload=payload,
        creado_por=creado_por,
        ip_origen=ip_origen,
        user_agent=user_agent,
    )


def auditar_cambio_cuota(
    *,
    odd,
    valor_anterior,
    valor_nuevo,
    cambiado_por=None,
    motivo=None,
    ip_origen=None,
    user_agent=None,
):
    """
    Registra en auditoría un cambio de cuota.
    """

    payload = {
        "odd_id": odd.id,
        "seleccion_id": odd.seleccion_id,
        "seleccion_nombre": odd.seleccion.nombre,
        "valor_anterior": str(valor_anterior),
        "valor_nuevo": str(valor_nuevo),
        "margen_operador": str(odd.margen_operador),
        "motivo": motivo,
        "fecha_actualizacion": str(odd.fecha_actualizacion),
    }

    return crear_registro_auditoria(
        tipo_evento=AuditLog.TipoEvento.ODD_CHANGED,
        entidad="Odd",
        entidad_id=odd.id,
        accion="updated",
        payload=payload,
        creado_por=cambiado_por,
        ip_origen=ip_origen,
        user_agent=user_agent,
    )


def auditar_juego_responsable(
    *,
    entidad,
    entidad_id,
    accion,
    payload,
    creado_por=None,
    ip_origen=None,
    user_agent=None,
):
    """
    Registra eventos de juego responsable:
    - autoexclusión creada
    - límite cambiado
    - bloqueo por autoexclusión
    """

    return crear_registro_auditoria(
        tipo_evento=AuditLog.TipoEvento.RESPONSIBLE_GAMING,
        entidad=entidad,
        entidad_id=entidad_id,
        accion=accion,
        payload=payload,
        creado_por=creado_por,
        ip_origen=ip_origen,
        user_agent=user_agent,
    )


def auditar_alerta_antifraude(
    *,
    entidad,
    entidad_id,
    accion,
    payload,
    creado_por=None,
    ip_origen=None,
    user_agent=None,
):
    """
    Registra alertas antifraude.
    """

    return crear_registro_auditoria(
        tipo_evento=AuditLog.TipoEvento.FRAUD_ALERT,
        entidad=entidad,
        entidad_id=entidad_id,
        accion=accion,
        payload=payload,
        creado_por=creado_por,
        ip_origen=ip_origen,
        user_agent=user_agent,
    )


def auditar_sesion_cuenta(
    *,
    usuario,
    accion,
    ip_origen=None,
    user_agent=None,
):
    payload = {
        "usuario_id": usuario.id,
        "username": usuario.username,
        "email": usuario.email,
        "accion": accion,
    }

    return crear_registro_auditoria(
        tipo_evento=AuditLog.TipoEvento.SYSTEM,
        entidad="UserSession",
        entidad_id=usuario.id,
        accion=accion,
        payload=payload,
        creado_por=usuario,
        ip_origen=ip_origen,
        user_agent=user_agent,
    )


def ejecutar_verificacion_integridad(*, ejecutado_por=None):
    """
    Ejecuta la verificación de integridad de la cadena de auditoría
    y guarda el resultado en AuditIntegrityCheck.
    """

    resultado = verificar_integridad_cadena()

    return AuditIntegrityCheck.objects.create(
        ejecutado_por=ejecutado_por,
        es_valida=resultado["es_valida"],
        total_registros=resultado["total_registros"],
        errores_detectados=resultado["errores"],
    )
