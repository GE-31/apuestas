from decimal import Decimal

from django.db import migrations


def subir_limites_legacy(apps, schema_editor):
    LimiteDeposito = apps.get_model("juego_responsable", "LimiteDeposito")
    LimiteDeposito.objects.filter(
        limite_diario=Decimal("100.0000"),
        limite_semanal=Decimal("500.0000"),
        limite_mensual=Decimal("1000.0000"),
    ).update(
        limite_diario=Decimal("1000.0000"),
        limite_semanal=Decimal("3000.0000"),
        limite_mensual=Decimal("10000.0000"),
    )


def bajar_limites_legacy(apps, schema_editor):
    LimiteDeposito = apps.get_model("juego_responsable", "LimiteDeposito")
    LimiteDeposito.objects.filter(
        limite_diario=Decimal("1000.0000"),
        limite_semanal=Decimal("3000.0000"),
        limite_mensual=Decimal("10000.0000"),
    ).update(
        limite_diario=Decimal("100.0000"),
        limite_semanal=Decimal("500.0000"),
        limite_mensual=Decimal("1000.0000"),
    )


class Migration(migrations.Migration):

    dependencies = [
        ("juego_responsable", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(subir_limites_legacy, bajar_limites_legacy),
    ]
