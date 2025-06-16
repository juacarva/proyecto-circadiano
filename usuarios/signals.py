from django.dispatch import receiver
# CAMBIO 1: Importamos la señal correcta.
from allauth.account.signals import email_confirmed
from django.contrib import messages

# CAMBIO 2: Usamos el decorador de la nueva señal.
@receiver(email_confirmed)
def email_confirmed_receiver(request, email_address, **kwargs):
    """
    Esta función se ejecuta en el preciso instante en que un usuario
    confirma exitosamente su dirección de correo electrónico.
    """
    # Obtenemos el usuario a través del objeto email_address
    user = email_address.user
    nombre_display = user.first_name or user.email

    # Creamos el mensaje de éxito.
    # allauth iniciará sesión automáticamente después de esto (comportamiento por defecto).
    messages.success(request, f"¡Gracias por confirmar tu correo, {nombre_display}! Tu cuenta ya está activa.")