from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction

_TIPO_DOC = [
    ('DNI',  'DNI'),
    ('CE',   'Carné de extranjería'),
    ('PASS', 'Pasaporte'),
]

_GENERO = [
    ('',  'Género'),
    ('M', 'Masculino'),
    ('F', 'Femenino'),
    ('X', 'Prefiero no indicar'),
]

_DEPARTAMENTOS = [
    ('',               'Departamento'),
    ('Amazonas',       'Amazonas'),
    ('Áncash',         'Áncash'),
    ('Apurímac',       'Apurímac'),
    ('Arequipa',       'Arequipa'),
    ('Ayacucho',       'Ayacucho'),
    ('Cajamarca',      'Cajamarca'),
    ('Callao',         'Callao'),
    ('Cusco',          'Cusco'),
    ('Huancavelica',   'Huancavelica'),
    ('Huánuco',        'Huánuco'),
    ('Ica',            'Ica'),
    ('Junín',          'Junín'),
    ('La Libertad',    'La Libertad'),
    ('Lambayeque',     'Lambayeque'),
    ('Lima',           'Lima'),
    ('Loreto',         'Loreto'),
    ('Madre de Dios',  'Madre de Dios'),
    ('Moquegua',       'Moquegua'),
    ('Pasco',          'Pasco'),
    ('Piura',          'Piura'),
    ('Puno',           'Puno'),
    ('San Martín',     'San Martín'),
    ('Tacna',          'Tacna'),
    ('Tumbes',         'Tumbes'),
    ('Ucayali',        'Ucayali'),
]


class LoginClienteForm(AuthenticationForm):
    """
    Formulario de login para clientes regulares.
    Hereda de AuthenticationForm de Django: valida credenciales
    contra la base de datos y verifica que la cuenta esté activa.
    """

    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={
            'placeholder': 'Tu nombre de usuario',
            'autocomplete': 'username',
            'class': 'form-input',
        })
    )

    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••',
            'autocomplete': 'current-password',
            'class': 'form-input',
        })
    )

    error_messages = {
        'invalid_login': (
            'Usuario o contraseña incorrectos. '
            'Verifica que tu usuario sea correcto.'
        ),
        'inactive': 'Tu cuenta está inactiva. Contacta al administrador.',
    }


class LoginAdminForm(AuthenticationForm):
    """
    Formulario de login para administradores y staff.
    Igual a AuthenticationForm pero con etiquetas corporativas.
    La verificación de permisos staff/superuser se realiza en la vista,
    no en el formulario — el formulario solo valida credenciales.
    """

    username = forms.CharField(
        label='Usuario administrador',
        widget=forms.TextInput(attrs={
            'placeholder': 'Usuario del sistema',
            'autocomplete': 'username',
            'class': 'admin-form-input',
        })
    )

    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••',
            'autocomplete': 'current-password',
            'class': 'admin-form-input',
        })
    )

    error_messages = {
        'invalid_login': (
            'Credenciales incorrectas. '
            'Solo personal autorizado puede acceder a este panel.'
        ),
        'inactive': 'Esta cuenta está inactiva.',
    }


class RegistroClienteForm(forms.Form):
    """Crea un User de Django + PerfilUsuario en una sola transacción."""

    tipo_documento   = forms.ChoiceField(choices=_TIPO_DOC, initial='DNI', label='Tipo de documento')
    dni              = forms.CharField(max_length=12, label='Número de documento')
    nombres          = forms.CharField(max_length=100, label='Nombres')
    apellidos        = forms.CharField(max_length=100, label='Apellidos')
    fecha_nacimiento = forms.DateField(
        label='Fecha de nacimiento',
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': ' '}),
    )
    genero           = forms.ChoiceField(choices=_GENERO, required=False, label='Género')
    email            = forms.EmailField(label='Correo electrónico')
    username         = forms.CharField(max_length=150, label='Nombre de usuario')
    password         = forms.CharField(
        min_length=8, label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': ' ', 'data-pwd-toggle-target': ''}),
    )
    confirm_password = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': ' ', 'data-pwd-toggle-target': ''}),
    )
    direccion        = forms.CharField(max_length=200, required=False, label='Dirección actual')
    departamento     = forms.ChoiceField(choices=_DEPARTAMENTOS, required=False, label='Departamento')
    provincia        = forms.CharField(max_length=100, required=False, label='Provincia')
    distrito         = forms.CharField(max_length=100, required=False, label='Distrito')
    telefono         = forms.CharField(max_length=15, required=False, label='Celular')
    pep              = forms.ChoiceField(
        choices=[('no', 'no'), ('si', 'si')],
        initial='no',
        widget=forms.RadioSelect,
        label='Declaración PEP',
    )
    acepta_terminos  = forms.BooleanField(
        required=True,
        error_messages={'required': 'Debes aceptar los Términos y Condiciones para continuar.'},
    )

    # ── Validaciones ──

    def clean(self):
        cd  = super().clean()
        pwd = cd.get('password')
        cfm = cd.get('confirm_password')
        if pwd and cfm and pwd != cfm:
            self.add_error('confirm_password', 'Las contraseñas no coinciden.')
        return cd

    def clean_dni(self):
        from usuarios.models import PerfilUsuario
        tipo = self.data.get('tipo_documento', 'DNI')
        dni  = self.cleaned_data.get('dni', '').strip()
        if tipo == 'DNI':
            if not dni.isdigit() or len(dni) != 8:
                raise forms.ValidationError('El DNI peruano debe tener exactamente 8 dígitos numéricos.')
        if not dni:
            raise forms.ValidationError('El número de documento es obligatorio.')
        if PerfilUsuario.objects.filter(dni=dni).exists():
            raise forms.ValidationError('Ya existe una cuenta registrada con este número de documento.')
        return dni

    def clean_username(self):
        User     = get_user_model()
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso. Elige otro.')
        return username

    def clean_email(self):
        User  = get_user_model()
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe una cuenta registrada con este correo electrónico.')
        return email

    # ── Guardar ──

    def save(self):
        from usuarios.models import PerfilUsuario
        User = get_user_model()
        cd   = self.cleaned_data
        partes = [p for p in [
            cd.get('direccion', ''),
            cd.get('distrito', ''),
            cd.get('provincia', ''),
            cd.get('departamento', ''),
        ] if p]
        full_dir = ', '.join(partes)
        with transaction.atomic():
            user = User.objects.create_user(
                username   = cd['username'],
                email      = cd['email'].lower(),
                password   = cd['password'],
                first_name = cd['nombres'],
                last_name  = cd['apellidos'],
            )
            from config.choices import EstadoCuenta
            PerfilUsuario.objects.create(
                usuario          = user,
                dni              = cd['dni'],
                nombres          = cd['nombres'],
                apellidos        = cd['apellidos'],
                fecha_nacimiento = cd['fecha_nacimiento'],
                telefono         = cd.get('telefono') or '',
                direccion        = full_dir,
                estado_cuenta    = EstadoCuenta.VERIFICADO,
            )
        return user
