# mensajeria/context_processors.py

from .models import Message, Conversation
from django.db.models import Q, OuterRef # <-- Importa OuterRef directamente
from django.db.models import Exists # También es útil importar Exists para un patrón común
from django.db import models # <-- Aquí sí importamos 'models' para usarlo directamente si es necesario, pero no de django.db.models

def unread_messages_count(request):
    """
    Context processor para añadir el número de mensajes no leídos del usuario
    y si tiene alguna conversación con mensajes no leídos al contexto de todas las plantillas.
    """
    unread_count = 0
    has_unread_conversations = False

    if request.user.is_authenticated:
        # Contar mensajes no leídos que el usuario ha recibido y aún no ha marcado como leídos
        # Excluye mensajes enviados por el propio usuario.
        unread_count = Message.objects.filter(
            conversation__participants=request.user, # La conversación debe ser del usuario
            is_read=False # El mensaje no debe estar leído
        ).exclude(
            sender=request.user # El mensaje no debe haber sido enviado por el propio usuario
        ).count()

        # Verificar si existe al menos una conversación con mensajes no leídos para el usuario
        has_unread_conversations = Conversation.objects.filter(
            participants=request.user
        ).filter(
            # Verifica que la conversación tiene mensajes no leídos por el usuario actual
            messages__is_read=False,
            # Ahora models.OuterRef debería ser reconocido
            messages__sender__in=Conversation.objects.filter(pk=models.OuterRef('pk')).values('participants').exclude(pk=request.user.pk) # Que el remitente no sea yo mismo
        ).exists()

    return {
        'unread_messages_count': unread_count,
        'has_unread_messages_overall': has_unread_conversations 
    }