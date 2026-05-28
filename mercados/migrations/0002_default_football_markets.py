from decimal import Decimal

from django.db import migrations


def create_selection_with_odd(apps, mercado, tipo, nombre, valor):
    SeleccionMercado = apps.get_model('mercados', 'SeleccionMercado')
    Odd = apps.get_model('cuotas', 'Odd')

    seleccion, _ = SeleccionMercado.objects.get_or_create(
        mercado=mercado,
        tipo=tipo,
        defaults={
            'nombre': nombre,
            'activo': True,
        },
    )
    Odd.objects.get_or_create(
        seleccion=seleccion,
        defaults={
            'valor': Decimal(valor),
            'margen_operador': Decimal('0'),
            'activa': True,
            'suspendida': False,
            'actualizada_por': None,
        },
    )


def forwards(apps, schema_editor):
    Account = apps.get_model('billetera', 'Account')
    Evento = apps.get_model('eventos', 'Evento')
    Mercado = apps.get_model('mercados', 'Mercado')
    PerfilUsuario = apps.get_model('usuarios', 'PerfilUsuario')

    Account.objects.get_or_create(
        usuario=None,
        tipo='casa',
        defaults={'nombre': 'Casa', 'activa': True},
    )
    Account.objects.get_or_create(
        usuario=None,
        tipo='apuestas_pendientes',
        defaults={'nombre': 'Apuestas pendientes', 'activa': True},
    )
    PerfilUsuario.objects.exclude(estado_cuenta='bloqueado').update(estado_cuenta='verificado')

    for evento in Evento.objects.select_related('equipo_local', 'equipo_visitante').filter(activo=True):
        local = evento.equipo_local.nombre
        visitante = evento.equipo_visitante.nombre
        specs = [
            ('over_under_05', 'Goles totales Mas/Menos 0.5', [
                ('over_05', 'Mas de 0.5 goles', '1.0800'),
                ('under_05', 'Menos de 0.5 goles', '7.5000'),
            ]),
            ('over_under_15', 'Goles totales Mas/Menos 1.5', [
                ('over_15', 'Mas de 1.5 goles', '1.3500'),
                ('under_15', 'Menos de 1.5 goles', '3.1000'),
            ]),
            ('over_under_25', 'Goles totales Mas/Menos 2.5', [
                ('over_25', 'Mas de 2.5 goles', '1.8500'),
                ('under_25', 'Menos de 2.5 goles', '1.9500'),
            ]),
            ('over_under_35', 'Goles totales Mas/Menos 3.5', [
                ('over_35', 'Mas de 3.5 goles', '3.2000'),
                ('under_35', 'Menos de 3.5 goles', '1.3300'),
            ]),
            ('double_chance', 'Doble oportunidad', [
                ('local_empate', f'{local} o Empate', '1.3500'),
                ('local_visitante', f'{local} o {visitante}', '1.2800'),
                ('empate_visitante', f'Empate o {visitante}', '1.5500'),
            ]),
            ('draw_no_bet', 'Apuesta sin empate', [
                ('local', local, '1.7000'),
                ('visitante', visitante, '2.1000'),
            ]),
            ('btts', 'Ambos equipos anotan', [
                ('ambos_si', 'Si', '1.9000'),
                ('ambos_no', 'No', '1.8500'),
            ]),
            ('exact_goals', 'Cantidad exacta de goles', [
                ('exact_0', '0 goles', '9.0000'),
                ('exact_1', '1 gol', '4.5000'),
                ('exact_2', '2 goles', '3.4000'),
                ('exact_3', '3 goles', '4.2000'),
                ('exact_4_plus', '4+ goles', '3.8000'),
            ]),
        ]
        for tipo, nombre, selecciones in specs:
            mercado, _ = Mercado.objects.get_or_create(
                evento=evento,
                tipo=tipo,
                defaults={
                    'nombre': nombre,
                    'activo': True,
                    'suspendido': False,
                },
            )
            for sel_tipo, sel_nombre, odd_valor in selecciones:
                create_selection_with_odd(apps, mercado, sel_tipo, sel_nombre, odd_valor)


class Migration(migrations.Migration):

    dependencies = [
        ('billetera', '0001_initial'),
        ('cuotas', '0001_initial'),
        ('eventos', '0003_fix_mojibake_names'),
        ('mercados', '0001_initial'),
        ('usuarios', '0002_perfil_dni_max_length_12'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
