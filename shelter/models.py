from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings  # Crítico para apuntar a AUTH_USER_MODEL

class Species(models.Model):
    """
    Representa las distintas especies de animales que maneja el refugio.
    Ejemplos: 'Perro', 'Gato', 'Conejo'.
    """
    
    name = models.CharField(max_length=50, unique=True, verbose_name="Nombre de la Especie")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Especie"
        verbose_name_plural = "Especies"
        ordering = ['name']

    def __str__(self):
        return self.name


class Race(models.Model):
    """
    Representa las distintas razas asociadas de forma directa a una especie.
    Ejemplos: 'Labrador' (vinculado a la especie Perro).
    """

    name = models.CharField(max_length=50, unique=True, verbose_name="Nombre de la Raza")
    
    species = models.ForeignKey(
        Species,
        on_delete=models.PROTECT,
        related_name='races',
        verbose_name="Especie"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Raza"
        verbose_name_plural = "Razas"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.species.name})"


class Pet(models.Model):
    """
    Representa a cada una de las mascotas individuales disponibles para adopción.
    """

    STATUS_CHOICES = [
        ('AVAILABLE', 'Disponible'),
        ('PENDING', 'En Proceso'),
        ('ADOPTED', 'Adoptado'),
    ]

    name = models.CharField(max_length=100, verbose_name="Nombre")
    
    species = models.ForeignKey(
        Species, 
        on_delete=models.PROTECT, 
        related_name='pets', 
        verbose_name="Especie"
    )
    
    race = models.ForeignKey(
        Race,
        on_delete=models.PROTECT,
        related_name='pets',
        verbose_name="Raza",
        null=True,
        blank=True
    )
    
    age_months = models.IntegerField(
        validators=[MinValueValidator(0)], 
        verbose_name="Edad (meses)"
    )
    
    description = models.TextField(blank=True, verbose_name="Descripción")
    image = models.ImageField(upload_to='pets/', blank=True, null=True, verbose_name="Foto")
    
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='AVAILABLE', 
        verbose_name="Estado"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mascota"
        verbose_name_plural = "Mascotas"
        ordering = ['-created_at']

    def __str__(self):
        race_name = self.race.name if self.race else "Mestizo"
        return f"{self.name} - {self.species.name} ({race_name})"


class AdoptionApplication(models.Model):
    """
    Representa la postulación de un adoptante interesado en una mascota específica.
    """

    STATUS_CHOICES = [
        ('REVIEW', 'En Revisión'),
        ('APPROVED', 'Aprobada'),
        ('REJECTED', 'Rechazada'),
    ]

    pet = models.ForeignKey(
        Pet, 
        on_delete=models.CASCADE, 
        related_name='applications', 
        verbose_name="Mascota"
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='applications',
        verbose_name="Usuario Adoptante"
    )
    
    motivation = models.TextField(verbose_name="¿Por qué desea adoptar?")
    
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='REVIEW', 
        verbose_name="Estado de la Solicitud"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Solicitud de Adopción"
        verbose_name_plural = "Solicitudes de Adopción"
        ordering = ['-created_at']

    def __str__(self):
        full_name = self.user.get_full_name()
        return f"Solicitud de {full_name or self.user.username} para {self.pet.name}"