from django.db import models


class EstadoCuenta(models.TextChoices):
    PENDIENTE_VERIFICACION = 'pendiente_verificacion', 'Pendiente de verificación'
    VERIFICADO = 'verificado', 'Verificado'
    BLOQUEADO = 'bloqueado', 'Bloqueado'
    AUTOEXCLUIDO = 'autoexcluido', 'Autoexcluido'


class TipoCuentaLedger(models.TextChoices):
    WALLET_USUARIO = 'wallet_usuario', 'Wallet de usuario'
    CASA = 'casa', 'Casa'
    APUESTAS_PENDIENTES = 'apuestas_pendientes', 'Apuestas pendientes'
    BONOS = 'bonos', 'Bonos'


class DireccionLedger(models.TextChoices):
    DEBIT = 'DEBIT', 'Débito'
    CREDIT = 'CREDIT', 'Crédito'


class TipoTransaccionLedger(models.TextChoices):
    RECARGA = 'recarga', 'Recarga simulada'
    RETIRO = 'retiro', 'Retiro simulado'
    TRANSFERENCIA = 'transferencia', 'Transferencia interna'
    BLOQUEO_APUESTA = 'bloqueo_apuesta', 'Bloqueo por apuesta'
    LIQUIDACION_APUESTA = 'liquidacion_apuesta', 'Liquidación de apuesta'
    CASHOUT = 'cashout', 'Cash-out'
    BONO = 'bono', 'Bono promocional'


class EstadoEvento(models.TextChoices):
    PROGRAMADO = 'programado', 'Programado'
    EN_VIVO = 'en_vivo', 'En vivo'
    FINALIZADO = 'finalizado', 'Finalizado'
    SUSPENDIDO = 'suspendido', 'Suspendido'
    ANULADO = 'anulado', 'Anulado'


class TipoMercado(models.TextChoices):
    UNO_X_DOS = '1x2', '1X2'
    OVER_UNDER = 'over_under', 'Over/Under'
    BTTS = 'btts', 'Ambos equipos anotan'
    HANDICAP = 'handicap', 'Handicap'


class TipoSeleccionMercado(models.TextChoices):
    LOCAL = 'local', 'Gana local'
    EMPATE = 'empate', 'Empate'
    VISITANTE = 'visitante', 'Gana visitante'
    OVER_25 = 'over_25', 'Más de 2.5 goles'
    UNDER_25 = 'under_25', 'Menos de 2.5 goles'
    AMBOS_SI = 'ambos_si', 'Ambos anotan'
    AMBOS_NO = 'ambos_no', 'Ambos no anotan'


class EstadoApuesta(models.TextChoices):
    BORRADOR = 'borrador', 'Borrador'
    ACCEPTED = 'accepted', 'Aceptada'
    WON = 'won', 'Ganada'
    LOST = 'lost', 'Perdida'
    CANCELLED = 'cancelled', 'Cancelada'
    CASHED_OUT = 'cashed_out', 'Cash-out'
    VOID = 'void', 'Anulada'


class TipoApuesta(models.TextChoices):
    SIMPLE = 'simple', 'Simple'
    COMBINADA = 'combinada', 'Combinada'


class EstadoAutoexclusion(models.TextChoices):
    ACTIVA = 'activa', 'Activa'
    FINALIZADA = 'finalizada', 'Finalizada'


class DuracionAutoexclusion(models.TextChoices):
    SIETE_DIAS = '7_dias', '7 días'
    TREINTA_DIAS = '30_dias', '30 días'
    NOVENTA_DIAS = '90_dias', '90 días'
    INDEFINIDA = 'indefinida', 'Indefinida'


class TipoAuditoria(models.TextChoices):
    BET = 'bet', 'Apuesta'
    WALLET = 'wallet', 'Wallet'
    ODDS = 'odds', 'Cuotas'
    USUARIO = 'usuario', 'Usuario'
    SISTEMA = 'sistema', 'Sistema'


class EstadoAlertaFraude(models.TextChoices):
    ABIERTA = 'abierta', 'Abierta'
    EN_REVISION = 'en_revision', 'En revisión'
    DESCARTADA = 'descartada', 'Descartada'
    CONFIRMADA = 'confirmada', 'Confirmada'


class SeveridadFraude(models.TextChoices):
    BAJA = 'baja', 'Baja'
    MEDIA = 'media', 'Media'
    ALTA = 'alta', 'Alta'
    CRITICA = 'critica', 'Crítica'