# mensajeria/admin.py

from django.contrib import admin
from .models import Conversation, Message

class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_participants', 'created_at', 'updated_at', 'is_archived') # <-- Añadido 'is_archived'
    list_filter = ('is_archived', 'created_at', 'updated_at') # <-- Añadido filtro por 'is_archived'
    filter_horizontal = ('participants',)
    search_fields = ('participants__username',)
    readonly_fields = ('created_at', 'updated_at')

    def display_participants(self, obj):
        return ", ".join([p.username for p in obj.participants.all()])
    display_participants.short_description = "Participantes"

    # --- Acciones personalizadas para Archivar/Desarchivar ---
    actions = ['mark_as_archived', 'mark_as_unarchived']

    def mark_as_archived(self, request, queryset):
        queryset.update(is_archived=True)
    mark_as_archived.short_description = "Archivar conversaciones seleccionadas"

    def mark_as_unarchived(self, request, queryset):
        queryset.update(is_archived=False)
    mark_as_unarchived.short_description = "Desarchivar conversaciones seleccionadas"
    # --- Fin Acciones ---


class MessageAdmin(admin.ModelAdmin):
    # ... (Tu clase MessageAdmin permanece sin cambios) ...
    list_display = ('conversation', 'sender', 'timestamp', 'is_read', 'content_snippet')
    list_filter = ('is_read', 'timestamp', 'sender', 'conversation__is_archived') # Puedes filtrar por si la conversación está archivada
    search_fields = ('content', 'sender__username')
    raw_id_fields = ('sender', 'conversation')

    def content_snippet(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_snippet.short_description = "Contenido"
    
    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Marcar como leído"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Marcar como no leído"


admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message, MessageAdmin)