from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Tarea(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tareas', null=True)
    texto   = models.CharField(max_length=255)
    hecha   = models.BooleanField(default=False)
    creada  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} — {self.texto}"


class PerfilPato(models.Model):
    usuario              = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_pato')
    nombre_pato          = models.CharField(max_length=50, blank=True, default="")
    puntos               = models.PositiveIntegerField(default=0)
    accesorios_comprados = models.JSONField(default=list, blank=True)
    accesorios_equipados = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name        = "Perfil de Pato"
        verbose_name_plural = "Perfiles de Pato"
        ordering            = ['-puntos']

    def __str__(self):
        nombre = self.nombre_pato or "Sin nombre"
        return f"{self.usuario.username} — 🦆 {nombre} ({self.puntos} pts)"

    @property
    def tareas_cumplidas(self):
        return self.usuario.tareas.filter(hecha=True).count()

    @property
    def tareas_pendientes(self):
        return self.usuario.tareas.filter(hecha=False).count()


class Mensaje(models.Model):
    """Mensaje de chat guardado en BD."""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensajes')
    sala    = models.CharField(max_length=120, db_index=True)  # 'global' | 'dm_alice_bob'
    texto   = models.TextField(max_length=1000)
    creado  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering            = ['creado']
        verbose_name        = "Mensaje"
        verbose_name_plural = "Mensajes"
        indexes             = [models.Index(fields=['sala', 'creado'])]

    def __str__(self):
        return f"[{self.sala}] {self.usuario.username}: {self.texto[:50]}"


@receiver(post_save, sender=User)
def crear_perfil_pato(sender, instance, created, **kwargs):
    if created:
        PerfilPato.objects.create(usuario=instance)