from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0003_future_demo_match_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='evento',
            name='periodo_en_vivo',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='evento',
            name='periodo_inicio',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
