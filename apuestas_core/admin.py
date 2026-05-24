from django.contrib import admin
from .models import Bet, BetSelection

# Register your models here.




class BetSelectionInline(admin.TabularInline):
    model = BetSelection
    extra = 0
    readonly_fields = (
        'seleccion',
        'odd',
        'odd_valor_tomado',
        'resultado',
        'fecha_creacion',
    )
    can_delete = False


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'usuario',
        'tipo',
        'estado',
        'stake',
        'odds_total',
        'payout_potencial',
        'payout_final',
        'aceptada_en',
        'liquidada_en',
        'fecha_creacion',
    )
    list_filter = (
        'tipo',
        'estado',
        'fecha_creacion',
        'aceptada_en',
        'liquidada_en',
    )
    search_fields = (
        'usuario__username',
        'usuario__email',
        'idempotency_key',
        'ip_origen',
    )
    readonly_fields = (
        'fecha_creacion',
        'fecha_actualizacion',
        'aceptada_en',
        'liquidada_en',
    )
    ordering = (
        '-fecha_creacion',
    )
    autocomplete_fields = (
        'usuario',
    )
    inlines = [
        BetSelectionInline,
    ]


@admin.register(BetSelection)
class BetSelectionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'bet',
        'seleccion',
        'odd',
        'odd_valor_tomado',
        'resultado',
        'fecha_creacion',
    )
    list_filter = (
        'resultado',
        'fecha_creacion',
    )
    search_fields = (
        'bet__usuario__username',
        'seleccion__nombre',
        'seleccion__mercado__nombre',
        'seleccion__mercado__evento__nombre',
    )
    readonly_fields = (
        'fecha_creacion',
    )
    ordering = (
        '-fecha_creacion',
    )
    autocomplete_fields = (
        'bet',
        'seleccion',
        'odd',
    )