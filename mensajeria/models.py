# mensajeria/models.py

from django.db import models
from django.contrib.auth.models import User # Importamos el modelo de usuario de Django (django.contrib.auth.models.User)
from django.utils import timezone # Para manejar fechas y horas

class Conversation(models.Model):
    """
    Representa un hilo de conversación entre dos o más usuarios.
    """
    # ManyToManyField para los participantes: una conversación puede tener muchos usuarios,
    # y un usuario puede participar en muchas conversaciones.
    # related_name='conversations' permite acceder a las conversaciones de un usuario (ej. user.conversations.all())
    participants = models.ManyToManyField(User, related_name='conversations', verbose_name="Participantes")
    
    # auto_now_add=True: Establece la fecha y hora de creación automáticamente la primera vez que se guarda el objeto.
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    # auto_now=True: Actualiza la fecha y hora automáticamente cada vez que se guarda el objeto.
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actividad")

    is_archived = models.BooleanField(default=False, verbose_name="¿Archivada?")

    class Meta:
        verbose_name = "Conversación"
        verbose_name_plural = "Conversaciones"
        ordering = ['-updated_at'] # Ordenar las conversaciones por la última actividad (las más recientes primero)

    def __str__(self):
        # Genera un string representativo de la conversación para el panel de administración y depuración.
        # Manejamos el caso de que no haya participantes (aunque no debería ocurrir en uso normal)
        usernames = [p.username for p in self.participants.all()]
        if len(usernames) > 2:
            return f"Conversación con {', '.join(usernames[:2])} y otros..."
        elif len(usernames) == 2:
            return f"Conversación entre {usernames[0]} y {usernames[1]}"
        elif len(usernames) == 1:
            return f"Conversación con {usernames[0]}"
        else:
            return "Conversación Vacía"

    def get_other_participant(self, current_user):
        """
        Método de ayuda: Devuelve el otro participante en una conversación de 2 personas.
        Útil para mostrar 'Conversación con [Nombre del Otro Usuario]' en la interfaz de usuario.
        Retorna None si la conversación no tiene exactamente 2 participantes.
        """
        if self.participants.count() == 2:
            # Excluye al usuario actual para obtener el "otro" participante
            return self.participants.exclude(pk=current_user.pk).first()
        return None # No aplica para conversaciones de grupo o sin participantes

class Message(models.Model):
    """
    Representa un mensaje individual dentro de una conversación específica.
    """
    # ForeignKey a Conversation: Cada mensaje pertenece a una única conversación.
    # on_delete=models.CASCADE: Si se elimina la conversación, todos sus mensajes también se eliminarán.
    # related_name='messages' permite acceder a los mensajes de una conversación (ej. conversation.messages.all())
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', verbose_name="Conversación")
    
    # ForeignKey a User (remitente): Indica quién envió este mensaje.
    # related_name='sent_messages' permite acceder a los mensajes enviados por un usuario (ej. user.sent_messages.all())
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name="Remitente")
    
    content = models.TextField(verbose_name="Contenido del Mensaje")
    
    # auto_now_add=True: Establece la fecha y hora de envío automáticamente la primera vez que se guarda el objeto.
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Marca de Tiempo")
    
    # is_read: Para rastrear si el mensaje ha sido leído por los destinatarios.
    is_read = models.BooleanField(default=False, verbose_name="¿Leído?")

    class Meta:
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"
        # Ordenar los mensajes cronológicamente dentro de una conversación
        ordering = ['timestamp'] 

    def __str__(self):
        # Representación de cadena para el mensaje, útil en el admin y depuración.
        return f"Mensaje de {self.sender.username} en '{self.conversation.id}' a las {self.timestamp.strftime('%H:%M')}"