from django.db import migrations


def forwards(apps, schema_editor):
    SeleccionMercado = apps.get_model('mercados', 'SeleccionMercado')

    replacements = {
        'Gana Per??????': 'Gana Perú',
        'Per?????? o Empate': 'Perú o Empate',
        'Per?????? o Argentina': 'Perú o Argentina',
        'Per??????': 'Perú',
    }
    for old, new in replacements.items():
        SeleccionMercado.objects.filter(nombre=old).update(nombre=new)


class Migration(migrations.Migration):

    dependencies = [
        ('mercados', '0002_default_football_markets'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
