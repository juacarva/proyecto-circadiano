from django.contrib import admin
from django.urls import path, include # Asegúrate de importar 'include'
from django.conf import settings # Importa settings
from django.conf.urls.static import static # Importa static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')), # <-- Ahora incluimos las URLs de tu app 'usuarios'
    path('', include('blog_circadiano.urls')), # Incluye las URLs de tu aplicación 'blog'
    path('messages/', include('mensajeria.urls')), # <-- ¡Añade esta línea para incluir las URLs de mensajería!
]

# Esto solo debe hacerse en desarrollo. En producción, tu servidor web (Nginx/Apache) servirá estos archivos.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)