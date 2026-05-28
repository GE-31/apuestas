from django.db import migrations
from django.utils import timezone


def forwards(apps, schema_editor):
    Evento = apps.get_model('eventos', 'Evento')
    nueva_fecha = timezone.datetime(2026, 6, 5, 19, 30, tzinfo=timezone.get_current_timezone())

    for evento in Evento.objects.select_related('equipo_local', 'equipo_visitante').filter(activo=True):
        evento.nombre = f'{evento.equipo_local.nombre} vs {evento.equipo_visitante.nombre}'
        if evento.fecha_inicio <= timezone.now():
            evento.fecha_inicio = nueva_fecha
            evento.estado = 'programado'
            evento.marcador_local = None
            evento.marcador_visitante = None
            evento.save(update_fields=['nombre', 'fecha_inicio', 'estado', 'marcador_local', 'marcador_visitante'])
        else:
            evento.save(update_fields=['nombre'])


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0002_liga'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
