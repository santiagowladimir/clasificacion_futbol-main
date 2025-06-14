from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db.models import Q
from django.core import validators
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
# models
from django.contrib.auth.models import User

from clubes.models import TIPO_ROL, TIPO_JUGADOR, Club, Torneo
from core.forms import FormBase, FormBaseUser, deshabilitar_campo
from core.funciones import generar_username
from core.validators import SoloLetras, v_cedulaform
from users.models import SEXO, Pais, PERFIL_USUARIO
from users.models.models_profile import UsuariosAcceso


class LoginForm(forms.Form):
    email = forms.CharField(label='Correo electrónico o nombre de usuario', widget=forms.TextInput())
    password = forms.CharField(label='Contraseña', max_length=70, widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].error_messages = {'required': f'Este campo es requerido'}

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        email = cleaned_data.get('email').lower()
        password = cleaned_data.get('password')
        if not User.objects.filter(Q(email=email) | (Q(username=email))).exists():
            self.add_error('email', 'No existe usuario con los datos ingresado.')
        else:
            usuario = User.objects.get(Q(email=email) | (Q(username=email)))
            cleaned_data['username'] = usuario.username
            if not usuario.is_active:
                self.add_error('email', 'Este usuario ha sido desactivado.')
            elif not check_password(password, usuario.password):
                self.add_error('password', 'Contraseña incorrecta.')
        return self.cleaned_data


class SignupForm(FormBaseUser):
    cedula = forms.CharField(label=u"Cédula", max_length=10, required=False,
                             widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Ingresa tu numero de cédula', 'class': 'soloNumeros'}))
    nombres = forms.CharField(label=u'Nombres', max_length=100, required=True,
                              widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Ingra tus nombres completos', 'class': 'soloLetrasET'}))
    apellido1 = forms.CharField(label=u"Primer apellido", max_length=50, required=True,
                                widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Ingresa tu primer apellido', 'class': 'soloLetrasET'}))
    apellido2 = forms.CharField(label=u"Segundo apellido", max_length=50, required=True,
                                widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Ingresa tu segundo apellido', 'class': 'soloLetrasET'}))
    fecha_nacimiento = forms.DateField(label=u'Fecha nacimiento', required=True,
                                       widget=forms.DateTimeInput(attrs={'col': '6'}))
    nacionalidad = forms.ModelChoiceField(label=u'Nacionalidad', required=False,
                                          queryset=Pais.objects.filter(status=True),
                                          widget=forms.Select(attrs={'col': '6'}))
    celular = forms.CharField(label=u"Teléfono celular", max_length=50, required=False,
                              widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Ingresa tu telefono celular', 'class': 'soloNumeros'}))
    email = forms.CharField(label=u"Correo electrónico", max_length=200, required=True,
                            widget=forms.EmailInput(attrs={'col': '6', 'placeholder': 'Ingresa tu correo electrónico'}))
    password = forms.CharField(label="Contraseña", max_length=70, widget=forms.PasswordInput(attrs={'col': '6', 'placeholder': 'Ingresa tu contraseña'}))
    password_confirmation = forms.CharField(label="Confirmar contraseña", max_length=70, widget=forms.PasswordInput(attrs={'col': '6', 'placeholder': 'Ingresa tu contraseña'}))

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = super().clean()
        password = data['password']
        password_confirmation = data['password_confirmation']
        # if 'cedula' in data and 'email' in data:
        #     cedula = data['cedula']
        #     email = data['email']
        #     ua=UsuariosAcceso.objects.filter(cedula=cedula, email=email, status=True).exists()
        #     if not ua:
        #         self.add_error('cedula','Usuario con los datos proporcionado no tienen permiso de registro')
        #         self.add_error('email','Usuario con los datos proporcionado no tienen permiso de registro')
        if len(password) >= 6:
            if password.islower() or password.isupper():
                msg = "La contraseña tiene que tener por lo menos 1 letra mayuscula y 1 minuscula"
                self.add_error('password', msg)
            if password.isdigit() or password.isalpha():
                msg = "La contraseña tiene que contener números, letras y caracteres especiales"
                self.add_error('password', msg)
        else:
            msg = "La contraseña tiene que tener como minimo 6 dígitos"
            self.add_error('password', msg)

        if password != password_confirmation:
            msg = "Contraseña no coincide"
            self.add_error('password_confirmation', msg)
        return data


class UsuarioForm(FormBaseUser):
    nombres = forms.CharField(label=u'Nombres', max_length=100, required=True,
                              widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Ingrese los nombres del administrativo', 'class': 'soloLetrasET'}))
    apellido1 = forms.CharField(label=u"Primer apellido", max_length=50, required=True,
                                widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Ingrese el primer apellido del administrativo', 'class': 'soloLetrasET'}))
    apellido2 = forms.CharField(label=u"Segundo apellido", max_length=50, required=True,
                                widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Ingrese el segundo apellido del administrativo', 'class': 'soloLetrasET'}))
    cedula = forms.CharField(label=u"Cédula", max_length=10, required=False,
                             widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Ingrese la cédula del administrativo', 'class': 'soloNumeros'}))
    fecha_nacimiento = forms.DateField(label=u'Fecha nacimiento', required=True,
                                       widget=forms.DateTimeInput(attrs={'col': '6'}))
    pasaporte = forms.CharField(label=u"Pasaporte", max_length=13, required=False,
                                widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Ingrese el pasaporte del administrativo'}))
    celular = forms.CharField(label=u"Teléfono celular", max_length=50, required=True,
                              widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Ingrese el teléfono celular del administrativo', 'class': 'soloNumeros'}))
    telefono = forms.CharField(label=u"Teléfono", max_length=50, required=False,
                               widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Ingrese el teléfono del administrativo (opcional)', 'class': 'soloNumeros'}))
    email = forms.CharField(label=u"Correo electrónico", max_length=200, required=True,
                            widget=forms.EmailInput(attrs={'col': '6', 'placeholder': 'Ingrese el correo electrónico del administrativo'}))
    sexo = forms.ChoiceField(label=u"Genero", required=True,
                             choices=SEXO,
                             widget=forms.Select(attrs={'col': '6'}))
    nacionalidad = forms.ModelChoiceField(label=u'Nacionalidad', required=False,
                                          queryset=Pais.objects.filter(status=True),
                                          widget=forms.Select(attrs={'col': '6'}))
    perfil = forms.ChoiceField(label=u'Perfil', required=True,
                               choices=PERFIL_USUARIO[1:4],
                               widget=forms.Select(attrs={'col': '6'}))
    direccion = forms.CharField(label=u"Dirección de domicilio", max_length=50, required=False,
                                widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Ingrese su dirección de calle principal'}))
    foto = forms.ImageField(label="Foto", required=False, widget=forms.FileInput(attrs={'col': '6'}))

    def edit(self):
        deshabilitar_campo(self, 'email')
        if self.instancia:
            cedula = getattr(self.instancia, 'cedula', None)
            pasaporte = getattr(self.instancia, 'pasaporte', None)
            if cedula:
                deshabilitar_campo(self, 'cedula')
            if pasaporte:
                deshabilitar_campo(self, 'pasaporte')

class UsuarioPermisoForm(FormBase):
    cedula = forms.CharField(label=u"Cédula", max_length=10, required=True,
                             widget=forms.TextInput(attrs={'col': '12', 'placeholder': 'Ingrese la cédula del administrativo', 'class': 'soloNumeros'}))
    email = forms.CharField(label=u"Correo electrónico", max_length=200, required=True,
                            widget=forms.EmailInput(attrs={'col': '12', 'placeholder': 'Ingrese el correo electrónico del administrativo'}))

    def clean(self):
       cleaned_data = super().clean()
       cedula=cleaned_data.get('cedula')
       email=cleaned_data.get('email')
       v_cedulaform(self, cedula, 'cedula')
       id = getattr(self.instancia, 'id', 0)

       ua=UsuariosAcceso.objects.filter(Q(cedula=cedula) | Q(email=email),status=True).exclude(id=id).exists()
       if ua:
           self.add_error('email', 'Registro que intenta agregar ya se encuentra creado')
           self.add_error('cedula', 'Registro que intenta agregar ya se encuentra creado')
       return cleaned_data

class PagoTarjetaForm(FormBase):
    torneo = forms.ModelChoiceField(label=u"Torneo", required=True,
                                    queryset=Torneo.objects.filter(status=True),
                                    widget=forms.Select(attrs={'col': '6', 'class': 'select2'}))
    equipo = forms.ModelChoiceField(label=u"Equipo", required=True,
                                  queryset=Club.objects.filter(status=True),
                                  widget=forms.Select(attrs={'col': '6', 'class': 'select2'}))
    codigo = forms.CharField(label=u"Código de equipo", max_length=10, required=True,
                            widget=forms.TextInput(attrs={'col': '6', 'placeholder': 'Código de su equipo proporcionado a su correo'}))
    valor = forms.CharField(label=u"Valor pagado", max_length=10, required=True,
                            widget=forms.TextInput(attrs={'col': '6', 'placeholder': '0.00'}))
    archivo = forms.FileField(label=u"Comprobante de pago", required=True,
                            widget=forms.FileInput(attrs={'col': '6',}))

    def clean(self):
       cleaned_data = super().clean()
       equipo=cleaned_data.get('equipo')
       codigo=cleaned_data.get('codigo')
       if not codigo == equipo.codigo:
           self.add_error('codigo','Código proporcionado no es el correcto')
       return cleaned_data
