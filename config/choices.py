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
    OVER_UNDER_05 = 'over_under_05', 'Mas/Menos 0.5 goles'
    OVER_UNDER_15 = 'over_under_15', 'Mas/Menos 1.5 goles'
    OVER_UNDER_25 = 'over_under_25', 'Mas/Menos 2.5 goles'
    OVER_UNDER_35 = 'over_under_35', 'Mas/Menos 3.5 goles'
    OVER_UNDER = 'over_under', 'Over/Under'
    BTTS = 'btts', 'Ambos equipos anotan'
    DOUBLE_CHANCE = 'double_chance', 'Doble oportunidad'
    DRAW_NO_BET = 'draw_no_bet', 'Apuesta sin empate'
    EXACT_GOALS = 'exact_goals', 'Cantidad exacta de goles'
    HANDICAP = 'handicap', 'Handicap'


class TipoSeleccionMercado(models.TextChoices):
    LOCAL = 'local', 'Gana local'
    EMPATE = 'empate', 'Empate'
    VISITANTE = 'visitante', 'Gana visitante'
    LOCAL_EMPATE = 'local_empate', 'Local o empate'
    LOCAL_VISITANTE = 'local_visitante', 'Local o visitante'
    EMPATE_VISITANTE = 'empate_visitante', 'Empate o visitante'
    OVER_05 = 'over_05', 'Mas de 0.5 goles'
    UNDER_05 = 'under_05', 'Menos de 0.5 goles'
    OVER_15 = 'over_15', 'Mas de 1.5 goles'
    UNDER_15 = 'under_15', 'Menos de 1.5 goles'
    OVER_25 = 'over_25', 'Más de 2.5 goles'
    UNDER_25 = 'under_25', 'Menos de 2.5 goles'
    OVER_35 = 'over_35', 'Mas de 3.5 goles'
    UNDER_35 = 'under_35', 'Menos de 3.5 goles'
    AMBOS_SI = 'ambos_si', 'Ambos anotan'
    AMBOS_NO = 'ambos_no', 'Ambos no anotan'
    EXACT_0 = 'exact_0', '0 goles'
    EXACT_1 = 'exact_1', '1 gol'
    EXACT_2 = 'exact_2', '2 goles'
    EXACT_3 = 'exact_3', '3 goles'
    EXACT_4_PLUS = 'exact_4_plus', '4+ goles'


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
