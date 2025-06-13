from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.template.defaultfilters import slugify # Para crear slugs automáticamente

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True) # Para URLs amigables

    class Meta:
        verbose_name_plural = "Categorías" # Para que aparezca "Categorías" en lugar de "Categorias" en el admin
        ordering = ['nombre']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

class Etiqueta(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True) # Para URLs amigables

    class Meta:
        ordering = ['nombre']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

class Articulo(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha_publicacion = models.DateTimeField(default=timezone.now)
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articulos')
    imagen_destacada = models.ImageField(upload_to='articulos/', blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='articulos_liked', blank=True)
    
    # ¡ESTOS SON LOS CAMPOS CLAVE QUE DEBEN ESTAR AQUÍ!
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='articulos')
    etiquetas = models.ManyToManyField(Etiqueta, blank=True, related_name='articulos')

    def __str__(self):
        return self.titulo

    @property
    def total_likes(self):
        return self.likes.count()

    class Meta:
        ordering = ['-fecha_publicacion']

class Comentario(models.Model):
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE, related_name='comentarios')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comentarios_realizados')
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(default=timezone.now)
    activo = models.BooleanField(default=True)
    # Campo para los likes del comentario (ManyToManyField para saber quién dio like)
    likes = models.ManyToManyField(User, related_name='comentarios_liked', blank=True)

    def __str__(self):
        if self.parent:
            return f'Respuesta de {self.autor.username} a "{self.parent.autor.username}" en "{self.articulo.titulo}"'
        return f'Comentario de {self.autor.username} en "{self.articulo.titulo}"'
    
    # Propiedad para obtener el número de likes del comentario
    @property
    def total_likes(self):
        return self.likes.count()

    class Meta:
        ordering = ['fecha_creacion']

    def is_parent(self):
        return self.parent is None