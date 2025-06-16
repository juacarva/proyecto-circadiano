# circadiano/usuarios/adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Este adaptador se ejecuta cuando un usuario inicia sesión a través de una cuenta social.

        Si un usuario inicia sesión con una cuenta social (ej. Google) y ya existe una
        cuenta local con la misma dirección de correo electrónico, esta función conectará
        automáticamente la cuenta social a la cuenta local existente. Esto evita que
        allauth pida al usuario que inicie sesión con su contraseña para demostrar la
        propiedad de la cuenta local.
        """
        # Si la cuenta social ya existe y está vinculada a un usuario, proceder normalmente.
        if sociallogin.is_existing:
            return

        # Comprobar si ya existe una cuenta de usuario con esta dirección de correo electrónico.
        # Confiamos en que el proveedor social (Google) ya ha verificado el correo.
        if 'email' in sociallogin.account.extra_data:
            email = sociallogin.account.extra_data['email']
            User = get_user_model()
            try:
                # Buscar un usuario existente con el mismo correo electrónico.
                existing_user = User.objects.get(email__iexact=email)
                
                # Conectar la cuenta social al usuario existente.
                sociallogin.connect(request, existing_user)
            except User.DoesNotExist:
                # Si no existe ningún usuario con este correo, continuar con el proceso
                # de registro normal. allauth creará un nuevo usuario.
                pass