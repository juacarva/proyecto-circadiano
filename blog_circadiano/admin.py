# blog_circadiano/admin.py

from django.contrib import admin
from .models import Articulo, Comentario, Categoria, Etiqueta

# Personalizar la visualización de Articulo en el admin
class ArticuloAdmin(admin.ModelAdmin):
    # Solución para admin.E108: 'categoria' se puede usar directamente en list_display
    # Solución para admin.E108: 'display_etiquetas' es un método que ya definiste
    list_display = ('titulo', 'autor', 'fecha_publicacion', 'categoria', 'display_etiquetas', 'total_likes')
    
    # Solución para admin.E116: Los campos de relación se pueden usar directamente en list_filter
    # Django es lo suficientemente inteligente para crear un filtro por relación.
    list_filter = ('fecha_publicacion', 'autor', 'categoria', 'etiquetas') # <-- No se necesita cambio aquí, el error es engañoso

    search_fields = ('titulo', 'contenido', 'autor__username', 'categoria__nombre', 'etiquetas__nombre') # Añadir búsqueda por nombre de categoría/etiqueta
    raw_id_fields = ('autor',) 
    
    # Método para mostrar las etiquetas como una cadena separada por comas
    def display_etiquetas(self, obj):
        return ", ".join([tag.nombre for tag in obj.etiquetas.all()])
    display_etiquetas.short_description = "Etiquetas"


# Personalizar la visualización de Comentario en el admin
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('autor', 'articulo', 'parent', 'fecha_creacion', 'activo', 'total_likes')
    list_filter = ('activo', 'fecha_creacion', 'autor', 'articulo')
    search_fields = ('autor__username', 'contenido')
    actions = ['make_active', 'make_inactive']

    def make_active(self, request, queryset):
        queryset.update(activo=True)
    make_active.short_description = "Marcar comentarios seleccionados como activos"

    def make_inactive(self, request, queryset):
        queryset.update(activo=False)
    make_inactive.short_description = "Marcar comentarios seleccionados como inactivos"


# Registrar los nuevos modelos
admin.site.register(Categoria)
admin.site.register(Etiqueta)

# Registrar los modelos existentes con sus clases Admin personalizadas
admin.site.register(Articulo, ArticuloAdmin)
admin.site.register(Comentario, ComentarioAdmin)