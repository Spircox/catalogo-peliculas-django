from django.db import models


class Titulo(models.Model):
    TIPO_CHOICES = [('pelicula', 'Película'), ('serie', 'Serie')]
    ESTADO_CHOICES = [('pendiente', 'Por ver'), ('viendo', 'Viendo'), ('vista', 'Vista')]

    tmdb_id = models.IntegerField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    nombre = models.CharField(max_length=200)
    sinopsis = models.TextField(blank=True)
    poster = models.URLField(blank=True)
    anio = models.CharField(max_length=10, blank=True)
    voto_tmdb = models.FloatField(default=0)
    generos = models.CharField(max_length=200, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    mi_nota = models.IntegerField(null=True, blank=True)
    comentario = models.TextField(blank=True)
    favorito = models.BooleanField(default=False)                      # ← NUEVO (5)
    fecha_vista = models.DateField(null=True, blank=True)              # ← NUEVO (6)
    duracion_min = models.IntegerField(default=0)                      # ← NUEVO (6)
    agregado_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-agregado_el']
        constraints = [models.UniqueConstraint(fields=['tmdb_id', 'tipo'], name='unico_tmdb_tipo')]

    def __str__(self):
        return self.nombre

    @property
    def generos_list(self):
        return [g for g in self.generos.split(', ') if g]

    @property
    def duracion_texto(self):
        if not self.duracion_min:
            return ''
        h, m = divmod(self.duracion_min, 60)
        return f'{h} h {m} min' if h else f'{m} min'