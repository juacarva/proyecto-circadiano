# mensajeria/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required # Para proteger las vistas
from django.views.decorators.http import require_POST # Para asegurar que la vista solo acepte POST
from django.contrib.auth.models import User # Para buscar usuarios al iniciar conversaciones
from django.db.models import Q, Max, Count # Q para OR, Max para última actividad, Count para contar participantes
from django.urls import reverse # Para redirigir usando nombres de URL
from django.http import JsonResponse, Http404 # Para respuestas JSON y manejo de 404
from django.db import transaction # Para asegurar operaciones atómicas en la BD
from django.utils import timezone

from .models import Conversation, Message # Importa los modelos que creaste
from .forms import MessageForm, StartConversationForm # Importa el formulario que acabas de crear

@login_required
def inbox(request):
    """
    Muestra la bandeja de entrada del usuario con una lista de sus conversaciones.
    Permite filtrar entre conversaciones activas y archivadas.
    """
    # Obtener el parámetro de filtro 'status' de la URL (ej. ?status=archived)
    conversation_status = request.GET.get('status', 'active') # 'active' por defecto

    conversations_qs = Conversation.objects.filter(participants=request.user)

    if conversation_status == 'active':
        conversations_qs = conversations_qs.filter(is_archived=False)
    elif conversation_status == 'archived':
        conversations_qs = conversations_qs.filter(is_archived=True)
    # Si 'all', no se filtra por is_archived

    conversations = conversations_qs.annotate(
        last_message_time=Max('messages__timestamp')
    ).filter(
        messages__isnull=False # Solo conversaciones con al menos un mensaje
    ).order_by('-last_message_time', '-updated_at')

    for conversation in conversations:
        conversation.other_participant_obj = conversation.get_other_participant(request.user)
        conversation.has_unread_messages = conversation.messages.filter(
            is_read=False
        ).exclude(
            sender=request.user
        ).exists()

    context = {
        'conversations': conversations,
        'conversation_status': conversation_status, # Pasa el estado actual a la plantilla
    }
    return render(request, 'mensajeria/inbox.html', context)

@login_required
def conversation_detail(request, conversation_id):
    """
    Muestra los mensajes de una conversación específica o crea una nueva
    al enviar el primer mensaje.
    """
    conversation = None
    recipient_username = request.GET.get('recipient_username') # Obtener el username del destinatario si es nueva conv.

    if conversation_id == 0: # Caso de nueva conversación (ID 0 es un marcador)
        if not recipient_username:
            return redirect('mensajeria:inbox') # Si no hay recipient_username, no sabemos con quién iniciar
        
        recipient = get_object_or_404(User, username=recipient_username)
        if recipient == request.user: # No iniciar conversación consigo mismo
            return redirect('mensajeria:inbox')

        # Si el POST es para una nueva conversación:
        if request.method == 'POST':
            form = MessageForm(request.POST)
            if form.is_valid():
                with transaction.atomic(): # Asegura que la creación y el mensaje sean atómicos
                    # Crea la nueva conversación aquí, solo si hay un mensaje para enviar
                    conversation = Conversation.objects.create()
                    conversation.participants.add(request.user, recipient)
                    # No es necesario conversation.save() aquí

                    message = form.save(commit=False)
                    message.conversation = conversation
                    message.sender = request.user
                    message.is_read = False # El mensaje es nuevo, así que no está leído por el receptor
                    message.save()
                    
                    # Actualizar la fecha de última actividad de la conversación
                    conversation.updated_at = timezone.now()
                    conversation.save() # Guarda para que updated_at se actualice después del add

                return redirect('mensajeria:conversation_detail', conversation_id=conversation.id)
        
        # Si no es POST y es nueva conversación (solo GET para mostrar el formulario vacío):
        form = MessageForm()
        context = {
            'conversation': None, # No hay conversación real todavía
            'messages': [], # No hay mensajes
            'form': form,
            'other_participant': recipient, # Mostrar con quién se va a iniciar
            'is_new_conversation': True, # Para control en plantilla
        }
        return render(request, 'mensajeria/conversation_detail.html', context)

    else: # Caso de conversación existente
        conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
        messages = conversation.messages.all()

        Message.objects.filter(conversation=conversation, is_read=False).exclude(sender=request.user).update(is_read=True)

        form = MessageForm()

        if request.method == 'POST':
            form = MessageForm(request.POST)
            if form.is_valid():
                message = form.save(commit=False)
                message.conversation = conversation
                message.sender = request.user
                message.is_read = False
                message.save()
                
                conversation.updated_at = timezone.now()
                conversation.save()

                return redirect('mensajeria:conversation_detail', conversation_id=conversation.id)
        
        context = {
            'conversation': conversation,
            'messages': messages,
            'form': form,
            'other_participant': conversation.get_other_participant(request.user),
            'is_new_conversation': False,
        }
        return render(request, 'mensajeria/conversation_detail.html', context)


@login_required
def start_new_conversation(request, username=None):
    """
    Permite iniciar una nueva conversación.
    - Si se proporciona un username en la URL, intenta iniciar la conversación directa.
    - Si no se proporciona username (GET a /messages/new/), muestra un formulario para buscar un usuario.
    - Si se envía el formulario (POST a /messages/new/), busca al usuario e inicia la conversación.
    """
    if username: # Si el username viene en la URL (ej. desde el perfil del autor)
        # Lógica existente para iniciar conversación directa
        recipient = get_object_or_404(User, username=username)
        if recipient == request.user:
            return redirect('mensajeria:inbox') # No conversar con uno mismo

        existing_conversation = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=recipient
        ).annotate(num_participants=Count('participants')).filter(num_participants=2).first()

        if existing_conversation:
            return redirect('mensajeria:conversation_detail', conversation_id=existing_conversation.id)
        
        # Redirigir a la vista de detalle para crear la conversación al enviar el primer mensaje
        return redirect(reverse('mensajeria:conversation_detail', kwargs={'conversation_id': 0}) + f'?recipient_username={recipient.username}')

    else: # Si no hay username en la URL (GET a /messages/new/)
        search_results = []
        if request.method == 'POST': # Cuando el usuario envía el formulario de búsqueda
            form = StartConversationForm(request.POST)
            if form.is_valid():
                search_query = form.cleaned_data['username']
                # Buscar usuarios que coincidan, excluyendo al propio usuario
                search_results = User.objects.filter(
                    Q(username__icontains=search_query) | Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query)
                ).exclude(
                    pk=request.user.pk # No mostrarse a sí mismo
                ).order_by('username')
                
                # Opcional: Si solo hay un resultado exacto, redirigir directamente
                if search_results.count() == 1 and search_results.first().username == search_query:
                    return redirect('mensajeria:start_new_conversation_with_user', username=search_results.first().username)
        else: # Si es una solicitud GET a /messages/new/
            form = StartConversationForm()
        
        context = {
            'form': form,
            'search_results': search_results,
        }
        return render(request, 'mensajeria/start_new_conversation.html', context)
    
@login_required
@require_POST
def toggle_archive_conversation(request):
    """
    Vista para archivar o desarchivar una conversación a través de AJAX.
    """
    user = request.user
    conversation_id = request.POST.get('conversation_id')

    if not conversation_id:
        return JsonResponse({'status': 'error', 'message': 'ID de conversación no proporcionado.'}, status=400)

    try:
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        # Asegurarse de que el usuario actual es un participante de la conversación
        if not conversation.participants.filter(id=user.id).exists():
            return JsonResponse({'status': 'error', 'message': 'No tienes permiso para archivar esta conversación.'}, status=403)

        # Invertir el estado de archivado
        conversation.is_archived = not conversation.is_archived
        conversation.save()

        return JsonResponse({
            'status': 'success',
            'is_archived': conversation.is_archived, # Nuevo estado
            'message': 'Conversación archivada' if conversation.is_archived else 'Conversación desarchivada'
        })

    except Http404:
        return JsonResponse({'status': 'error', 'message': 'Conversación no encontrada.'}, status=404)
    except Exception as e:
        print(f"Error inesperado en toggle_archive_conversation: {e}")
        return JsonResponse({'status': 'error', 'message': 'Ocurrió un error interno del servidor.'}, status=500)