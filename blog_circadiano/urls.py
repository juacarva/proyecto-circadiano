# blog_circadiano/urls.py

from django.urls import path
from . import views
from .models import Categoria, Etiqueta # Importa los modelos para pasarlos al contexto global si es necesario
from .views import GuiaWrapperView, DocumentoDetalladoView


app_name = 'blog_circadiano'

urlpatterns = [

    path('nosotros/', views.nosotros, name='nosotros'),

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

     # 1. URL que el usuario visita (el marco)
    path('articulo/<int:pk>/guia/', GuiaWrapperView.as_view(), name='vista_guia'),
    
    # 2. URL para el contenido del iframe (la guía en sí)
    path('articulo/<int:pk>/guia/contenido/', views.guia_contenido_view, name='vista_guia_contenido'),

    path('articulo/<int:pk>/documento/', DocumentoDetalladoView.as_view(), name='vista_documento'),

    # ¡NUEVAS URLs PARA LAS SERIES!
    path('series/', views.lista_series, name='lista_series'),
    path('series/<slug:serie_slug>/', views.detalle_serie, name='detalle_serie'),
]