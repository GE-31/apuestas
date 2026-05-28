from decimal import Decimal

from django.db import migrations
from django.utils import timezone


def get_or_create_team(apps, deporte, nombre, pais):
    Equipo = apps.get_model('eventos', 'Equipo')
    equipo, _ = Equipo.objects.get_or_create(
        deporte=deporte,
        nombre=nombre,
        defaults={
            'pais': pais,
            'activo': True,
        },
    )
    updates = []
    if equipo.pais != pais:
        equipo.pais = pais
        updates.append('pais')
    if not equipo.activo:
        equipo.activo = True
        updates.append('activo')
    if updates:
        equipo.save(update_fields=updates)
    return equipo


def set_odd(apps, mercado, tipo, nombre, valor):
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
    changed = []
    if seleccion.nombre != nombre:
        seleccion.nombre = nombre
        changed.append('nombre')
    if not seleccion.activo:
        seleccion.activo = True
        changed.append('activo')
    if changed:
        seleccion.save(update_fields=changed)

    odd, _ = Odd.objects.get_or_create(
        seleccion=seleccion,
        defaults={
            'valor': Decimal(valor),
            'margen_operador': Decimal('0.0000'),
            'activa': True,
            'suspendida': False,
            'actualizada_por': None,
        },
    )
    odd.valor = Decimal(valor)
    odd.activa = True
    odd.suspendida = False
    odd.save(update_fields=['valor', 'activa', 'suspendida', 'fecha_actualizacion'])


def ensure_market(apps, evento, tipo, nombre, selections):
    Mercado = apps.get_model('mercados', 'Mercado')
    mercado, _ = Mercado.objects.get_or_create(
        evento=evento,
        tipo=tipo,
        defaults={
            'nombre': nombre,
            'activo': True,
            'suspendido': False,
        },
    )
    updates = []
    if mercado.nombre != nombre:
        mercado.nombre = nombre
        updates.append('nombre')
    if not mercado.activo:
        mercado.activo = True
        updates.append('activo')
    if mercado.suspendido:
        mercado.suspendido = False
        updates.append('suspendido')
    if updates:
        mercado.save(update_fields=updates)

    for tipo_sel, nombre_sel, valor in selections:
        set_odd(apps, mercado, tipo_sel, nombre_sel, valor)


def forwards(apps, schema_editor):
    Deporte = apps.get_model('eventos', 'Deporte')
    Liga = apps.get_model('eventos', 'Liga')
    Evento = apps.get_model('eventos', 'Evento')

    futbol, _ = Deporte.objects.get_or_create(
        nombre='Fútbol',
        defaults={'descripcion': '', 'activo': True},
    )

    libertadores, _ = Liga.objects.get_or_create(
        deporte=futbol,
        nombre='Copa Libertadores',
        defaults={'pais': 'CONMEBOL', 'activa': True},
    )
    sudamericana, _ = Liga.objects.get_or_create(
        deporte=futbol,
        nombre='Copa Sudamericana',
        defaults={'pais': 'CONMEBOL', 'activa': True},
    )

    tz = timezone.get_current_timezone()
    matches = [
        {
            'liga': libertadores,
            'local': ('Cruzeiro', 'Brasil'),
            'visitante': ('Barcelona SC', 'Ecuador'),
            'fecha': timezone.datetime(2026, 5, 28, 19, 30, tzinfo=tz),
            'one_x_two': ('1.3100', '5.4000', '13.5000'),
            'over_under_25': ('1.8800', '1.9300'),
            'btts': ('2.4500', '1.5000'),
        },
        {
            'liga': sudamericana,
            'local': ('CA Tigre', 'Argentina'),
            'visitante': ('Alianza Atlético', 'Perú'),
            'fecha': timezone.datetime(2026, 5, 28, 19, 30, tzinfo=tz),
            'one_x_two': ('1.3100', '5.4000', '13.5000'),
            'over_under_25': ('1.8800', '1.9300'),
            'btts': ('2.4500', '1.5000'),
        },
        {
            'liga': libertadores,
            'local': ('Boca Juniors', 'Argentina'),
            'visitante': ('Universidad Católica', 'Chile'),
            'fecha': timezone.datetime(2026, 5, 28, 19, 30, tzinfo=tz),
            'one_x_two': ('1.3100', '5.4000', '13.5000'),
            'over_under_25': ('1.8800', '1.9300'),
            'btts': ('2.4500', '1.5000'),
        },
        {
            'liga': libertadores,
            'local': ('Cerro Porteño', 'Paraguay'),
            'visitante': ('Sporting Cristal', 'Perú'),
            'fecha': timezone.datetime(2026, 5, 28, 17, 0, tzinfo=tz),
            'one_x_two': ('1.3100', '5.4000', '13.5000'),
            'over_under_25': ('1.8800', '1.9300'),
            'btts': ('2.4500', '1.5000'),
        },
    ]

    for item in matches:
        local = get_or_create_team(apps, futbol, item['local'][0], item['local'][1])
        visitante = get_or_create_team(apps, futbol, item['visitante'][0], item['visitante'][1])
        evento, _ = Evento.objects.get_or_create(
            deporte=futbol,
            equipo_local=local,
            equipo_visitante=visitante,
            fecha_inicio=item['fecha'],
            defaults={
                'liga': item['liga'],
                'nombre': f'{local.nombre} vs {visitante.nombre}',
                'estado': 'programado',
                'activo': True,
            },
        )
        evento.liga = item['liga']
        evento.nombre = f'{local.nombre} vs {visitante.nombre}'
        evento.estado = 'programado'
        evento.activo = True
        evento.marcador_local = None
        evento.marcador_visitante = None
        evento.save(update_fields=[
            'liga',
            'nombre',
            'estado',
            'activo',
            'marcador_local',
            'marcador_visitante',
            'fecha_actualizacion',
        ])

        local_odd, draw_odd, visitante_odd = item['one_x_two']
        ensure_market(apps, evento, '1x2', 'Resultado final 1X2', [
            ('local', f'Gana {local.nombre}', local_odd),
            ('empate', 'Empate', draw_odd),
            ('visitante', f'Gana {visitante.nombre}', visitante_odd),
        ])

        over_odd, under_odd = item['over_under_25']
        ensure_market(apps, evento, 'over_under_25', 'Goles totales Mas/Menos 2.5', [
            ('over_25', 'Mas de 2.5 goles', over_odd),
            ('under_25', 'Menos de 2.5 goles', under_odd),
        ])

        yes_odd, no_odd = item['btts']
        ensure_market(apps, evento, 'btts', 'Ambos equipos anotan', [
            ('ambos_si', 'Si', yes_odd),
            ('ambos_no', 'No', no_odd),
        ])


class Migration(migrations.Migration):

    dependencies = [
        ('cuotas', '0001_initial'),
        ('eventos', '0003_future_demo_match_date'),
        ('mercados', '0003_update_market_choices'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
