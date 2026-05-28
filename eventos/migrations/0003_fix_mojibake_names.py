from django.db import migrations


def forwards(apps, schema_editor):
    Deporte = apps.get_model('eventos', 'Deporte')
    Liga = apps.get_model('eventos', 'Liga')
    Equipo = apps.get_model('eventos', 'Equipo')

    Deporte.objects.filter(nombre__contains='?').update(nombre='Fútbol')
    Deporte.objects.filter(nombre__iexact='futbol').update(nombre='Fútbol')
    Deporte.objects.filter(nombre__iexact='basquetbol').update(nombre='Básquetbol')
    Liga.objects.filter(pais__contains='?').update(pais='Perú')
    Liga.objects.filter(pais__iexact='peru').update(pais='Perú')
    Equipo.objects.filter(nombre__contains='?').update(nombre='Perú')
    Equipo.objects.filter(pais__contains='?').update(pais='Perú')
    Equipo.objects.filter(nombre__iexact='peru').update(nombre='Perú')
    Equipo.objects.filter(pais__iexact='peru').update(pais='Perú')


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0002_liga'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
