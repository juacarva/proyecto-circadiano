from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required # Para requerir inicio de sesión
from django.urls import reverse # Para construir URLs dinámicamente
from django.http import JsonResponse, Http404 # Importar para respuestas AJAX
from django.views.decorators.http import require_POST # Para asegurar que la vista solo acepte POST
from django.db.models import Q # <-- ¡Importa Q para búsquedas complejas!

from .models import Articulo, Comentario, Categoria, Etiqueta
from .forms import ComentarioForm # Importa tu formulario de comentarios


def lista_articulos(request, categoria_slug=None, etiqueta_slug=None):
    articulos_qs = Articulo.objects.all() # Queryset base para todos los artículos
    
    categoria = None
    etiqueta = None
    query = None # Variable para almacenar el término de búsqueda

    if categoria_slug:
        categoria = get_object_or_404(Categoria, slug=categoria_slug)
        articulos_qs = articulos_qs.filter(categoria=categoria)
    
    if etiqueta_slug:
        etiqueta = get_object_or_404(Etiqueta, slug=etiqueta_slug)
        articulos_qs = articulos_qs.filter(etiquetas=etiqueta)

    # --- Lógica de Búsqueda por Palabra Clave ---
    if 'q' in request.GET:
        query = request.GET.get('q')
        if query: # Si el término de búsqueda no está vacío
            # Filtra artículos donde el título o el contenido contengan el término (case-insensitive)
            articulos_qs = articulos_qs.filter(
                Q(titulo__icontains=query) | Q(contenido__icontains=query)
            )
    # --- Fin Lógica de Búsqueda ---

    articulos = articulos_qs.order_by('-fecha_publicacion') # Asegura el orden por fecha

    todas_categorias = Categoria.objects.all()
    todas_etiquetas = Etiqueta.objects.all()

    context = {
        'articulos': articulos,
        'categoria_actual': categoria,
        'etiqueta_actual': etiqueta,
        'todas_categorias': todas_categorias,
        'todas_etiquetas': todas_etiquetas,
        'show_sidebar': True, # Mostrar sidebar en la lista de artículos
        'query': query, # <-- Pasa el término de búsqueda a la plantilla para mantenerlo en el campo
    }
    return render(request, 'blog_circadiano/lista_articulos.html', context)

# ... (resto de tus vistas como detalle_articulo y toggle_like) ...

def detalle_articulo(request, pk):
    articulo = get_object_or_404(Articulo, pk=pk)
    
    comentarios = Comentario.objects.filter(
        articulo=articulo, 
        parent__isnull=True, 
        activo=True
    ).select_related('autor').prefetch_related(
        'replies__autor', 
        'replies__replies__autor', 
    )
    
    nuevo_comentario = None
    form = ComentarioForm()

    user_liked_article = False
    if request.user.is_authenticated:
        user_liked_article = articulo.likes.filter(id=request.user.id).exists()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(reverse('usuarios:login') + f'?next={request.path}')

        form = ComentarioForm(data=request.POST)
        if form.is_valid():
            nuevo_comentario = form.save(commit=False)
            nuevo_comentario.articulo = articulo
            nuevo_comentario.autor = request.user
            
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    parent_obj = Comentario.objects.get(id=parent_id)
                    nuevo_comentario.parent = parent_obj
                except Comentario.DoesNotExist:
                    pass
            
            nuevo_comentario.save()
            return redirect(reverse('blog_circadiano:detalle_articulo', kwargs={'pk': articulo.pk}) + f'#comentario-{nuevo_comentario.pk}')
    
    context = {
        'articulo': articulo,
        'comentarios': comentarios,
        'form': form,
        'user_liked_article': user_liked_article,
        'show_sidebar': False, # <-- ¡Añadido! No mostrar sidebar en el detalle del artículo
    }
    return render(request, 'blog_circadiano/detalle_articulo.html', context)

# Vista para manejar solo el envío de comentarios (podría ser redundante con la vista anterior,
# pero a veces se separa para más claridad o para API)
@login_required # Decorador para asegurar que solo usuarios logueados pueden acceder
def post_comentario(request, pk):
    articulo = get_object_or_404(Articulo, pk=pk)
    if request.method == 'POST':
        form = ComentarioForm(data=request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.articulo = articulo
            comentario.autor = request.user
            
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    parent_obj = Comentario.objects.get(id=parent_id)
                    comentario.parent = parent_obj
                except Comentario.DoesNotExist:
                    pass
            
            comentario.save()
            return redirect(reverse('blog_circadiano:detalle_articulo', kwargs={'pk': articulo.pk}) + f'#comentario-{comentario.pk}')
    
    # Si no es POST o el formulario no es válido, redirigir de nuevo a la página del artículo
    return redirect('blog_circadiano:detalle_articulo', pk=articulo.pk)

@login_required # Esto redirige a /usuarios/login/?next=... si no está logueado
@require_POST
def toggle_like(request):
    try:
        user = request.user
        item_type = request.POST.get('item_type')
        item_id = request.POST.get('item_id')

        # Validaciones de entrada
        if not item_type or not item_id:
            return JsonResponse({'status': 'error', 'message': 'Faltan parámetros: item_type o item_id.'}, status=400)
        
        if item_type not in ['articulo', 'comentario']:
            return JsonResponse({'status': 'error', 'message': 'Tipo de ítem inválido. Debe ser "articulo" o "comentario".'}, status=400)

        # Determinar el modelo y obtener el objeto
        item = None
        if item_type == 'articulo':
            item = get_object_or_404(Articulo, id=item_id) # get_object_or_404 lanza Http404 que convertiremos a JsonResponse
        elif item_type == 'comentario':
            item = get_object_or_404(Comentario, id=item_id) # get_object_or_404 lanza Http404

        # Lógica de toggle
        if user in item.likes.all():
            item.likes.remove(user)
            liked = False
        else:
            item.likes.add(user)
            liked = True
        
        return JsonResponse({'status': 'success', 'liked': liked, 'total_likes': item.total_likes})

    except Http404: # Captura si get_object_or_404 no encuentra el objeto
        return JsonResponse({'status': 'error', 'message': 'Ítem no encontrado.'}, status=404)
    except Exception as e:
        # Captura cualquier otra excepción inesperada
        print(f"Error inesperado en toggle_like: {e}") # Para ver en la consola del servidor
        # Si DEBUG es True, podrías considerar devolver un mensaje más detallado
        # en producción, un mensaje genérico de error interno.
        return JsonResponse({'status': 'error', 'message': 'Ocurrió un error interno del servidor.'}, status=500)