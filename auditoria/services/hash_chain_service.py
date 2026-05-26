import hashlib
import json

from django.db import transaction

from auditoria.models import AuditLog


class AuditHashError(Exception):
    pass


def normalizar_payload(payload):
    """
    Convierte el payload a JSON ordenado para que el hash sea estable.
    """

    return json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        default=str,
        separators=(",", ":"),
    )


def calcular_hash_auditoria(
    *,
    previous_hash,
    tipo_evento,
    entidad,
    entidad_id,
    accion,
    payload,
):
    """
    Calcula el hash del registro actual.

    Fórmula:
    hash_n = SHA256(hash_n-1 + payload_n)
    """

    payload_normalizado = normalizar_payload(payload)

    data = {
        "previous_hash": previous_hash or "",
        "tipo_evento": tipo_evento,
        "entidad": entidad,
        "entidad_id": str(entidad_id),
        "accion": accion,
        "payload": payload_normalizado,
    }

    data_normalizada = json.dumps(
        data,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    return hashlib.sha256(data_normalizada.encode("utf-8")).hexdigest()


def obtener_ultimo_audit_log():
    """
    Obtiene el último registro de auditoría creado.
    """

    return AuditLog.objects.order_by("-id").first()


@transaction.atomic
def crear_registro_auditoria(
    *,
    tipo_evento,
    entidad,
    entidad_id,
    accion,
    payload,
    creado_por=None,
    ip_origen=None,
    user_agent=None,
):
    """
    Crea un registro de auditoría append-only con hash encadenado.

    Importante:
    - No se actualizan registros anteriores.
    - Cada nuevo registro apunta al hash anterior.
    """

    ultimo_log = (
        AuditLog.objects
        .select_for_update()
        .order_by("-id")
        .first()
    )

    previous_hash = ultimo_log.current_hash if ultimo_log else None

    current_hash = calcular_hash_auditoria(
        previous_hash=previous_hash,
        tipo_evento=tipo_evento,
        entidad=entidad,
        entidad_id=entidad_id,
        accion=accion,
        payload=payload,
    )

    return AuditLog.objects.create(
        tipo_evento=tipo_evento,
        entidad=entidad,
        entidad_id=str(entidad_id),
        accion=accion,
        payload=payload,
        previous_hash=previous_hash,
        current_hash=current_hash,
        creado_por=creado_por,
        ip_origen=ip_origen,
        user_agent=user_agent,
    )


def recalcular_hash_log(log):
    """
    Recalcula el hash de un registro existente para verificar integridad.
    """

    return calcular_hash_auditoria(
        previous_hash=log.previous_hash,
        tipo_evento=log.tipo_evento,
        entidad=log.entidad,
        entidad_id=log.entidad_id,
        accion=log.accion,
        payload=log.payload,
    )


def verificar_integridad_cadena():
    """
    Verifica que la cadena de auditoría no haya sido alterada.

    Retorna:
    {
        "es_valida": bool,
        "total_registros": int,
        "errores": []
    }
    """

    logs = AuditLog.objects.order_by("id")

    errores = []
    previous_hash_esperado = None
    total = 0

    for log in logs:
        total += 1

        if log.previous_hash != previous_hash_esperado:
            errores.append({
                "id": log.id,
                "tipo": "previous_hash_invalido",
                "esperado": previous_hash_esperado,
                "actual": log.previous_hash,
            })

        current_hash_recalculado = recalcular_hash_log(log)

        if log.current_hash != current_hash_recalculado:
            errores.append({
                "id": log.id,
                "tipo": "current_hash_invalido",
                "esperado": current_hash_recalculado,
                "actual": log.current_hash,
            })

        previous_hash_esperado = log.current_hash

    return {
        "es_valida": len(errores) == 0,
        "total_registros": total,
        "errores": errores,
    }