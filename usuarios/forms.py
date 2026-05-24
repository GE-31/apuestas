from django import forms
from django.contrib.auth.forms import AuthenticationForm


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
