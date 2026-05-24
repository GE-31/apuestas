
from django.contrib import admin

from .models import Account, LedgerEntry, LedgerTransaction


class LedgerEntryInline(admin.TabularInline):
    model = LedgerEntry
    extra = 0
    readonly_fields = (
        'account',
        'amount',
        'direction',
        'descripcion',
        'fecha_creacion',
    )
    can_delete = False


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre',
        'tipo',
        'usuario',
        'activa',
        'fecha_creacion',
    )
    list_filter = (
        'tipo',
        'activa',
        'fecha_creacion',
    )
    search_fields = (
        'nombre',
        'usuario__username',
        'usuario__email',
    )
    readonly_fields = (
        'fecha_creacion',
        'fecha_actualizacion',
    )
    ordering = (
        'tipo',
        'nombre',
    )


@admin.register(LedgerTransaction)
class LedgerTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'tipo',
        'referencia',
        'idempotency_key',
        'creado_por',
        'fecha_creacion',
    )
    list_filter = (
        'tipo',
        'fecha_creacion',
    )
    search_fields = (
        'referencia',
        'idempotency_key',
        'descripcion',
        'creado_por__username',
    )
    readonly_fields = (
        'fecha_creacion',
    )
    ordering = (
        '-fecha_creacion',
    )
    inlines = [
        LedgerEntryInline,
    ]


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'transaction',
        'account',
        'direction',
        'amount',
        'fecha_creacion',
    )
    list_filter = (
        'direction',
        'fecha_creacion',
        'account__tipo',
    )
    search_fields = (
        'transaction__referencia',
        'transaction__idempotency_key',
        'account__nombre',
        'account__usuario__username',
    )
    readonly_fields = (
        'fecha_creacion',
    )
    ordering = (
        '-fecha_creacion',
    )