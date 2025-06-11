from django.urls import path
from . import views # Importa las vistas de tu aplicación actual

app_name = 'blog_circadiano' # Define un nombre de aplicación para la gestión de URLs

urlpatterns = [
    path('', views.lista_articulos, name='lista_articulos'), # URL para la lista de artículos
    path('articulo/<int:pk>/', views.detalle_articulo, name='detalle_articulo'), # URL para un artículo individual
]