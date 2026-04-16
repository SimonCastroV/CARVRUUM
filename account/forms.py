from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile
from django import forms
from .models import Profile, CIUDADES_COLOMBIA
# ------------------------------
# LOGIN FORM
# ------------------------------
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Usuario", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))


# ------------------------------
# REGISTER FORM
# ------------------------------
class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="Confirmar Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    telefono = forms.CharField(label="Teléfono", required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    CIUDADES_COLOMBIA = [
        ('', 'Seleccionar ciudad'),
        ('bogota', 'Bogotá'),
        ('medellin', 'Medellín'),
        ('cali', 'Cali'),
        ('barranquilla', 'Barranquilla'),
        ('cartagena', 'Cartagena'),
        ('cucuta', 'Cúcuta'),
        ('bucaramanga', 'Bucaramanga'),
        ('pereira', 'Pereira'),
        ('santamarta', 'Santa Marta'),
        ('manizales', 'Manizales'),
        ('ibague', 'Ibagué'),
        ('neiva', 'Neiva'),
        ('villavicencio', 'Villavicencio'),
        ('pasto', 'Pasto'),
        ('monteria', 'Montería'),
        ('popayan', 'Popayán'),
        ('sincelejo', 'Sincelejo'),
        ('valledupar', 'Valledupar'),
        ('armenia', 'Armenia'),
        ('riohacha', 'Riohacha'),
    ]

    ciudad_residencia = forms.ChoiceField(
        label="Ciudad de residencia",
        choices=CIUDADES_COLOMBIA,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


# ------------------------------
# USER FORM
# ------------------------------
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control rounded'}),
            'email': forms.EmailInput(attrs={'class': 'form-control rounded'}),
        }


# ------------------------------
# PROFILE FORM
# ------------------------------
class ProfileForm(forms.ModelForm):
    CIUDADES_COLOMBIA = [
        ('', 'Seleccionar ciudad'),
        ('bogota', 'Bogotá'),
        ('medellin', 'Medellín'),
        ('cali', 'Cali'),
        ('barranquilla', 'Barranquilla'),
        ('cartagena', 'Cartagena'),
        ('cucuta', 'Cúcuta'),
        ('bucaramanga', 'Bucaramanga'),
        ('pereira', 'Pereira'),
        ('santamarta', 'Santa Marta'),
        ('manizales', 'Manizales'),
        ('ibague', 'Ibagué'),
        ('neiva', 'Neiva'),
        ('villavicencio', 'Villavicencio'),
        ('pasto', 'Pasto'),
        ('monteria', 'Montería'),
        ('popayan', 'Popayán'),
        ('sincelejo', 'Sincelejo'),
        ('valledupar', 'Valledupar'),
        ('armenia', 'Armenia'),
        ('riohacha', 'Riohacha'),
    ]

    ciudad = forms.ChoiceField(
        label="Ciudad",
        choices=CIUDADES_COLOMBIA,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select rounded'})
    )

    class Meta:
        model = Profile
        fields = ['telefono', 'ciudad']
        widgets = {
            'telefono': forms.TextInput(attrs={'class': 'form-control rounded'}),
        }



class ProfileEditForm(forms.Form):
    telefono = forms.CharField(
        max_length=20,
        required=False,
        label="Teléfono",
        widget=forms.TextInput(attrs={
            "class": "w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
        })
    )
    ciudad = forms.ChoiceField(
        choices=[("", "— Selecciona una ciudad —")] + list(CIUDADES_COLOMBIA),
        required=False,
        label="Ciudad",
        widget=forms.Select(attrs={
            "class": "w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
        })
    )

    def __init__(self, *args, profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        if profile:
            self.fields["telefono"].initial = profile.telefono
            self.fields["ciudad"].initial   = profile.ciudad