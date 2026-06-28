from django.contrib.auth.models import AbstractUser
from django.db import models

class Role(models.Model):
    """
    Representa los roles del sistema dentro del refugio.
    Permite al administrador crear dinámicamente opciones como 'ADMIN', 'ADOPTANT', 'VET', etc.
    """
    code = models.CharField(max_length=20, unique=True, verbose_name="Código del Rol")
    name = models.CharField(max_length=50, verbose_name="Nombre del Rol")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ['name']

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    """
    Modelo personalizado de usuario que implementa roles dinámicos mediante base de datos.
    """

    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name='users',
        verbose_name="Rol de Usuario",
        null=True,
        blank=True
    )
    
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección")

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    @property
    def is_shelter_admin(self):
        if self.is_superuser:
            return True
        return self.role.code == 'ADMIN' if self.role else False

    def __str__(self):
        full_name = self.get_full_name()
        role_name = self.role.name if self.role else "Sin Rol"
        return f"{full_name or self.username} ({role_name})"