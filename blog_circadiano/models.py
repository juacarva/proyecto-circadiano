from django.db import models
from django.contrib.auth.models import User # Para relacionar artículos y comentarios con usuarios
from django.utils import timezone # Para fechas

class Articulo(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha_publicacion = models.DateTimeField(default=timezone.now)
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articulos')
    imagen_destacada = models.ImageField(upload_to='articulos/', blank=True, null=True) # Opcional: para imágenes

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ['-fecha_publicacion'] # Ordena los artículos por fecha de publicación descendente


class Comentario(models.Model):
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE, related_name='comentarios')
    # Clave foránea auto-referencial para los comentarios anidados
    # Un comentario puede tener un padre (el comentario al que responde)
    # parent=None significa que es un comentario de nivel superior
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comentarios_realizados')
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(default=timezone.now)
    activo = models.BooleanField(default=True) # Para moderar comentarios si lo deseas

    def __str__(self):
        if self.parent:
            return f'Respuesta de {self.autor.username} a "{self.parent.autor.username}" en "{self.articulo.titulo}"'
        return f'Comentario de {self.autor.username} en "{self.articulo.titulo}"'

    class Meta:
        ordering = ['fecha_creacion']

    # Método para verificar si es un comentario de nivel superior (no es una respuesta)
    def is_parent(self):
        return self.parent is None