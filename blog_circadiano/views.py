from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required # Para requerir inicio de sesión
from django.urls import reverse # Para construir URLs dinámicamente
from django.http import JsonResponse, Http404 # Importar para respuestas AJAX
from django.views.decorators.http import require_POST # Para asegurar que la vista solo acepte POST
from django.db.models import Max, Q # <-- ¡Importa Q para búsquedas complejas!
from django.views.generic import DetailView
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Articulo, Comentario, Categoria, Etiqueta,Serie
from .forms import ComentarioForm # Importa tu formulario de comentarios


# circadia/blog_circadiano/views.py

from django.shortcuts import render, get_object_or_404
from .models import Articulo, Categoria, Etiqueta, Serie # Asegúrate de importar Serie
from django.db.models import Q

def lista_articulos(request, categoria_slug=None, etiqueta_slug=None):
    """
    Vista que obtiene TODOS los artículos y permite que la plantilla
    muestre un marcador si pertenecen a una serie.
    """
    # 1. Empezamos con TODOS los artículos. Este es el cambio clave.
    articulos_qs = Articulo.objects.all() 
    
    categoria_actual = None
    etiqueta_actual = None
    query = request.GET.get('q')

    # 2. Aplicamos los filtros de categoría y etiqueta
    if categoria_slug:
        categoria_actual = get_object_or_404(Categoria, slug=categoria_slug)
        articulos_qs = articulos_qs.filter(categoria=categoria_actual)
    
    if etiqueta_slug:
        etiqueta_actual = get_object_or_404(Etiqueta, slug=etiqueta_slug)
        articulos_qs = articulos_qs.filter(etiquetas=etiqueta_actual)

    # 3. Aplicamos el filtro de búsqueda
    if query:
        articulos_qs = articulos_qs.filter(
            Q(titulo__icontains=query) | Q(contenido__icontains=query)
        )

    # 4. Ordenamos y preparamos el contexto final
    articulos = articulos_qs.order_by('-fecha_publicacion')

    todas_categorias = Categoria.objects.all()
    todas_etiquetas = Etiqueta.objects.all()

    context = {
        # La plantilla espera esta variable: 'articulos'
        'articulos': articulos, 
        'categoria_actual': categoria_actual,
        'etiqueta_actual': etiqueta_actual,
        'todas_categorias': todas_categorias,
        'todas_etiquetas': todas_etiquetas,
        'query': query,
        'show_sidebar': True, # <-- ¡ESTA ES LA LÍNEA QUE FALTABA!
    }
    return render(request, 'blog_circadiano/lista_articulos.html', context)

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
    

# 1. La vista que muestra el marco y el iframe (la que el usuario visita)
class GuiaWrapperView(DetailView):
    model = Articulo
    template_name = "blog_circadiano/guia_wrapper.html"
    pk_url_kwarg = 'pk'
    context_object_name = 'articulo' # Pasamos el artículo como 'articulo' al contexto

# 2. La vista que renderiza SOLO el contenido de la guía para el iframe
@xframe_options_sameorigin
def guia_contenido_view(request, pk):
    articulo = get_object_or_404(Articulo, pk=pk)
    
    if not articulo.guia_slug:
        raise Http404("Guía no encontrada.")

    template_name = f"blog_circadiano/guias/{articulo.guia_slug}"
    context = {
        'articulo': articulo,
        'titulo_guia': f"Guía para: {articulo.titulo}"
    }
    return render(request, template_name, context)

class DocumentoDetalladoView(LoginRequiredMixin, DetailView):
    model = Articulo
    # Esta es la plantilla que crearemos en el siguiente paso
    template_name = 'blog_circadiano/documento_detallado_page.html' 
    context_object_name = 'articulo'

def lista_series(request):
    """
    Vista para mostrar todas las series disponibles, incluyendo el sidebar.
    """
    series = Serie.objects.all()

    # --- LÍNEAS AÑADIDAS ---
    # Obtenemos los datos para el sidebar
    todas_categorias = Categoria.objects.all()
    todas_etiquetas = Etiqueta.objects.all()
    # -------------------------

    context = {
        'series': series,
        'todas_categorias': todas_categorias, # <-- Nueva variable
        'todas_etiquetas': todas_etiquetas,   # <-- Nueva variable
        'show_sidebar': False,               # <-- Variable para mostrar el sidebar
    }
    return render(request, 'blog_circadiano/lista_series.html', context)

def detalle_serie(request, serie_slug):
    """
    Vista para mostrar los artículos de una serie específica.
    """
    serie = get_object_or_404(Serie, slug=serie_slug)
    articulos_en_serie = serie.articulos.all().order_by('fecha_publicacion') # Ordenamos los artículos cronológicamente
    context = {
        'serie': serie,
        'articulos_en_serie': articulos_en_serie,
        'show_sidebar': False, # Tampoco mostramos el sidebar aquí
    }
    return render(request, 'blog_circadiano/detalle_serie.html', context)

def nosotros(request):
    return render(request, 'blog_circadiano/nosotros.html')
