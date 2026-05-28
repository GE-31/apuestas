from django.core.management.base import BaseCommand
from django.utils import timezone

from apuestas_core.models import Bet
from apuestas_core.services.cashout_service import calcular_oferta_cashout
from config.choices import EstadoApuesta


class Command(BaseCommand):
    help = 'Muestra diagnóstico de disponibilidad de cashout para apuestas.'

    def add_arguments(self, parser):
        parser.add_argument('--user-id', type=int, help='ID de usuario para filtrar apuestas')
        parser.add_argument('--bet-id', type=int, help='ID de apuesta específica')

    def handle(self, *args, **options):
        now = timezone.now()
        qs = Bet.objects.select_related('usuario').prefetch_related('selecciones__seleccion__mercado__evento')
        if options.get('bet_id'):
            qs = qs.filter(id=options['bet_id'])
        if options.get('user_id'):
            qs = qs.filter(usuario_id=options['user_id'])

        qs = qs.order_by('-fecha_creacion')[:50]

        if not qs.exists():
            self.stdout.write('No se encontraron apuestas con los filtros dados.')
            return

        for bet in qs:
            self.stdout.write(f'BET #{bet.id} usuario={bet.usuario_id} estado={bet.estado} stake={bet.stake}')
            eventos = [sel.seleccion.mercado.evento for sel in bet.selecciones.all()]
            if not eventos:
                self.stdout.write('  - Sin selecciones / eventos')
            for evento in eventos:
                self.stdout.write(f'  - Evento id={evento.id} estado={evento.estado} fecha_inicio={evento.fecha_inicio} (now={now})')
            try:
                oferta = calcular_oferta_cashout(bet)
            except Exception as exc:
                oferta = f'ERROR: {exc}'
            self.stdout.write(f'  -> oferta_cashout={oferta}')
