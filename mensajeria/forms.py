# mensajeria/forms.py

from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    """
    Formulario para enviar un nuevo mensaje.
    """
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escribe tu mensaje aquí...'}),
        }

class StartConversationForm(forms.Form):
    """
    Formulario para buscar un usuario con quien iniciar una nueva conversación.
    """
    username = forms.CharField(
        label="Nombre de usuario del destinatario",
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Ej: usuario123'})
    )