from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from apuestas_core.services.apuesta_service import crear_apuesta_simple
from billetera.services.deposito_service import recargar_fichas_usuario
from config.choices import EstadoEvento, TipoMercado, TipoSeleccionMercado
from cuotas.models import Odd
from eventos.models import Deporte, Equipo, Evento, Liga
from mercados.models import Mercado, SeleccionMercado


class DeporteAdminForm(forms.Form):
    nombre = forms.CharField(max_length=120, label='Nombre del deporte')
    descripcion = forms.CharField(max_length=255, required=False, label='Descripción (opcional)',
                                  widget=forms.TextInput())

    def save(self):
        return Deporte.objects.create(
            nombre=self.cleaned_data['nombre'],
            descripcion=self.cleaned_data.get('descripcion') or '',
            activo=True,
        )


class LigaAdminForm(forms.Form):
    deporte = forms.ModelChoiceField(queryset=Deporte.objects.filter(activo=True), label='Deporte')
    nombre = forms.CharField(max_length=120, label='Nombre de la liga')
    pais = forms.CharField(max_length=80, required=False, label='País (opcional)')

    def save(self):
        return Liga.objects.create(
            deporte=self.cleaned_data['deporte'],
            nombre=self.cleaned_data['nombre'],
            pais=self.cleaned_data.get('pais') or '',
            activa=True,
        )


class EquipoAdminForm(forms.Form):
    deporte = forms.ModelChoiceField(queryset=Deporte.objects.filter(activo=True), label='Deporte')
    nombre = forms.CharField(max_length=120, label='Equipo')
    abreviatura = forms.CharField(max_length=10, required=False, label='Abreviatura')
    pais = forms.CharField(max_length=80, required=False, label='Pais')

    def save(self):
        return Equipo.objects.create(
            deporte=self.cleaned_data['deporte'],
            nombre=self.cleaned_data['nombre'],
            abreviatura=self.cleaned_data.get('abreviatura') or '',
            pais=self.cleaned_data.get('pais') or '',
            activo=True,
        )


class EventoAdminForm(forms.Form):
    deporte = forms.ModelChoiceField(queryset=Deporte.objects.filter(activo=True), label='Deporte')
    liga = forms.ModelChoiceField(
        queryset=Liga.objects.filter(activa=True).select_related('deporte').order_by('deporte__nombre', 'nombre'),
        required=False,
        label='Liga (opcional)',
        empty_label='— Sin liga —',
    )
    equipo_local = forms.ModelChoiceField(queryset=Equipo.objects.filter(activo=True), label='Equipo local')
    equipo_visitante = forms.ModelChoiceField(queryset=Equipo.objects.filter(activo=True), label='Equipo visitante')
    fecha_inicio = forms.DateTimeField(
        label='Fecha y hora',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    )
    cuota_local = forms.DecimalField(max_digits=8, decimal_places=4, min_value=1.0001, initial='2.0000', label='Local')
    cuota_empate = forms.DecimalField(max_digits=8, decimal_places=4, min_value=1.0001, initial='3.2000', label='Empate')
    cuota_visitante = forms.DecimalField(max_digits=8, decimal_places=4, min_value=1.0001, initial='2.8000', label='Visitante')

    def clean(self):
        cleaned = super().clean()
        local = cleaned.get('equipo_local')
        visitante = cleaned.get('equipo_visitante')
        if local and visitante and local == visitante:
            self.add_error('equipo_visitante', 'El visitante debe ser diferente al local.')
        return cleaned

    def save(self, user):
        local = self.cleaned_data['equipo_local']
        visitante = self.cleaned_data['equipo_visitante']
        fecha_inicio = self.cleaned_data['fecha_inicio']
        if timezone.is_naive(fecha_inicio):
            fecha_inicio = timezone.make_aware(fecha_inicio, timezone.get_current_timezone())

        evento = Evento.objects.create(
            deporte=self.cleaned_data['deporte'],
            liga=self.cleaned_data.get('liga'),
            equipo_local=local,
            equipo_visitante=visitante,
            nombre=f'{local.nombre} vs {visitante.nombre}',
            estado=EstadoEvento.PROGRAMADO,
            fecha_inicio=fecha_inicio,
            activo=True,
        )

        mercado = Mercado.objects.create(
            evento=evento,
            tipo=TipoMercado.UNO_X_DOS,
            nombre='Resultado final 1X2',
            activo=True,
            suspendido=False,
        )

        selecciones = [
            (TipoSeleccionMercado.LOCAL, f'Gana {local.nombre}', self.cleaned_data['cuota_local']),
            (TipoSeleccionMercado.EMPATE, 'Empate', self.cleaned_data['cuota_empate']),
            (TipoSeleccionMercado.VISITANTE, f'Gana {visitante.nombre}', self.cleaned_data['cuota_visitante']),
        ]

        for tipo, nombre, valor in selecciones:
            seleccion = SeleccionMercado.objects.create(
                mercado=mercado,
                tipo=tipo,
                nombre=nombre,
                activo=True,
            )
            Odd.objects.create(
                seleccion=seleccion,
                valor=valor,
                margen_operador=0,
                activa=True,
                suspendida=False,
                actualizada_por=user,
            )

        return evento


class EventoLigaUpdateForm(forms.Form):
    evento_id = forms.IntegerField(widget=forms.HiddenInput())
    liga = forms.ModelChoiceField(
        queryset=Liga.objects.filter(activa=True).select_related('deporte').order_by('deporte__nombre', 'nombre'),
        required=False,
        label='Liga',
        empty_label='— Sin liga —',
    )

    def save(self):
        from eventos.models import Evento as _Evento
        evento = _Evento.objects.get(id=self.cleaned_data['evento_id'])
        evento.liga = self.cleaned_data.get('liga')
        evento.save(update_fields=['liga'])
        return evento


class RecargaAdminForm(forms.Form):
    usuario = forms.ModelChoiceField(
        queryset=get_user_model().objects.filter(
            is_active=True, is_staff=False, is_superuser=False
        ).order_by('username'),
        label='Cliente',
    )
    amount = forms.DecimalField(max_digits=18, decimal_places=4, min_value=0.0001, label='Monto S/')

    def save(self, user):
        return recargar_fichas_usuario(
            usuario=self.cleaned_data['usuario'],
            amount=self.cleaned_data['amount'],
            idempotency_key=f'admin-recarga-{timezone.now().timestamp()}',
            creado_por=user,
        )


class ApuestaAdminForm(forms.Form):
    usuario = forms.ModelChoiceField(
        queryset=get_user_model().objects.filter(is_active=True, is_staff=False).order_by('username'),
        label='Cliente',
    )
    odd = forms.ModelChoiceField(
        queryset=Odd.objects.filter(activa=True, suspendida=False).select_related('seleccion__mercado__evento'),
        label='Seleccion',
    )
    stake = forms.DecimalField(max_digits=18, decimal_places=4, min_value=1.0000, label='Monto S/')

    def save(self, request):
        return crear_apuesta_simple(
            usuario=self.cleaned_data['usuario'],
            odd_id=self.cleaned_data['odd'].id,
            stake=self.cleaned_data['stake'],
            idempotency_key=f'admin-apuesta-{timezone.now().timestamp()}',
            ip_origen=request.META.get('REMOTE_ADDR'),
        )
