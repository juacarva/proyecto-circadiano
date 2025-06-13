# blog_circadiano/urls.py

from django.urls import path
from . import views
from .models import Categoria, Etiqueta # Importa los modelos para pasarlos al contexto global si es necesario

app_name = 'blog_circadiano'

urlpatterns = [
    # URL principal para la lista de artículos (sin filtros)
    path('', views.lista_articulos, name='lista_articulos'),
    
    # URL para filtrar por categoría
    path('categoria/<slug:categoria_slug>/', views.lista_articulos, name='articulos_por_categoria'),
    
    # URL para filtrar por etiqueta
    path('etiqueta/<slug:etiqueta_slug>/', views.lista_articulos, name='articulos_por_etiqueta'),
    
    # URL para detalle de artículo
    path('articulo/<int:pk>/', views.detalle_articulo, name='detalle_articulo'),
    
    # URL para likes
    path('toggle_like/', views.toggle_like, name='toggle_like'),
]