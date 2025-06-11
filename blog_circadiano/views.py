from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required # Para requerir inicio de sesión
from django.urls import reverse # Para construir URLs dinámicamente

from .models import Articulo, Comentario
from .forms import ComentarioForm # Importa tu formulario de comentarios

def lista_articulos(request):
    articulos = Articulo.objects.all()
    context = {
        'articulos': articulos
    }
    return render(request, 'blog_circadiano/lista_articulos.html', context)

def detalle_articulo(request, pk):
    articulo = get_object_or_404(Articulo, pk=pk)
    
    # Optimizando la consulta de comentarios
    # Obtenemos los comentarios de nivel superior, y pre-cargamos sus respuestas
    # y los autores de esas respuestas.
    comentarios = Comentario.objects.filter(
        articulo=articulo, 
        parent__isnull=True, 
        activo=True
    ).select_related('autor').prefetch_related(
        'replies__autor', # Carga el autor de las respuestas
        'replies__replies__autor', # Y el autor de las respuestas a las respuestas
        # Puedes seguir añadiendo más niveles si tu profundidad máxima es conocida y limitada
        # o considerar un enfoque más avanzado para muchos niveles.
    )
    
    nuevo_comentario = None
    form = ComentarioForm()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('usuarios:login') # Asegúrate de que la URL de login sea correcta

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
        'user': request.user, # Asegúrate de pasar el objeto user a la plantilla
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