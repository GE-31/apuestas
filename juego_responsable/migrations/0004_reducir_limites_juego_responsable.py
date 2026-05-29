from decimal import Decimal

from django.db import migrations


def forwards(apps, schema_editor):
    LimiteDeposito = apps.get_model('juego_responsable', 'LimiteDeposito')
    LimiteDeposito.objects.all().update(
        limite_diario=Decimal('200.0000'),
        limite_semanal=Decimal('1000.0000'),
        limite_mensual=Decimal('3000.0000'),
    )


class Migration(migrations.Migration):

    dependencies = [
        ('juego_responsable', '0003_raise_deposit_limits'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
