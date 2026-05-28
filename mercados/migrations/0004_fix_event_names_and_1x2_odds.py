from decimal import Decimal

from django.db import migrations


def forwards(apps, schema_editor):
    Evento = apps.get_model('eventos', 'Evento')
    Odd = apps.get_model('cuotas', 'Odd')

    for evento in Evento.objects.select_related('equipo_local', 'equipo_visitante'):
        nombre = f'{evento.equipo_local.nombre} vs {evento.equipo_visitante.nombre}'
        if evento.nombre != nombre:
            evento.nombre = nombre
            evento.save(update_fields=['nombre'])

        mercado = evento.mercados.filter(tipo='1x2').first()
        if not mercado:
            continue

        defaults = {
            'empate': Decimal('3.2000'),
            'visitante': Decimal('2.8000'),
        }
        for seleccion in mercado.selecciones.all():
            valor = defaults.get(seleccion.tipo)
            if valor is None:
                continue
            Odd.objects.get_or_create(
                seleccion=seleccion,
                defaults={
                    'valor': valor,
                    'margen_operador': Decimal('0.0000'),
                    'activa': True,
                    'suspendida': False,
                    'actualizada_por': None,
                },
            )


class Migration(migrations.Migration):

    dependencies = [
        ('mercados', '0003_fix_mojibake_selection_names'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
