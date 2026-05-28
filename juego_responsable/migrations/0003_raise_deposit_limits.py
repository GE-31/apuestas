from decimal import Decimal

from django.db import migrations


def forwards(apps, schema_editor):
    LimiteDeposito = apps.get_model('juego_responsable', 'LimiteDeposito')
    LimiteDeposito.objects.all().update(
        limite_diario=Decimal('5000.0000'),
        limite_semanal=Decimal('25000.0000'),
        limite_mensual=Decimal('100000.0000'),
    )


class Migration(migrations.Migration):

    dependencies = [
        ('juego_responsable', '0002_actualizar_limites_default_pruebas'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
