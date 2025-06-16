from django import forms
from allauth.account.forms import SignupForm

class CustomSignupForm(SignupForm):
    """
    Formulario de registro personalizado que añade nombre/apellido y
    oculta de forma segura el texto de ayuda de la contraseña.
    """
    first_name = forms.CharField(max_length=30, label='Nombre', widget=forms.TextInput(attrs={'placeholder': 'Tu nombre'}))
    last_name = forms.CharField(max_length=30, label='Apellido', widget=forms.TextInput(attrs={'placeholder': 'Tu apellido'}))

    def __init__(self, *args, **kwargs):
        # Dejamos que el formulario original se construya primero.
        super().__init__(*args, **kwargs)
        
        # --- ESTA ES LA CORRECCIÓN CLAVE ---
        # Primero, PREGUNTAMOS si el campo existe antes de intentar modificarlo.
        if 'password' in self.fields:
            self.fields['password'].help_text = ''
        
        if 'password2' in self.fields:
            self.fields['password2'].help_text = ''
        # ------------------------------------

    def save(self, request):
        # La lógica para guardar el usuario se mantiene igual.
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user