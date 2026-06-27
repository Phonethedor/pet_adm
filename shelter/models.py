from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.

class Race(models.Model):
    """
    Representa las distintas razas de las especies que maneja el refugio.
    Permite al administrador crear dinámicamente opciones como 'Labrador', 'Calico', 'Monitor', etc.
    """
    name = models.CharField(max_length=50, unique=True, verbose_name="Nombre de la Raza")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Raza"
        verbose_name_plural = "Razas"
        ordering = ['name']

    def __str__(self):
        return self.name


class Species(models.Model):
    """
    Representa las distintas especies de animales que maneja el refugio.
    Permite al administrador crear dinámicamente opciones como 'Perro', 'Gato', 'Hurón', etc.
    """
    name = models.CharField(max_length=50, unique=True, verbose_name="Nombre de la Especie")

    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE,
        related_name='species',
        verbose_name="Raza"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Especie"
        verbose_name_plural = "Especies"
        ordering = ['name']

    def __str__(self):
        return self.name


class Pet(models.Model):
    """
    Representa a cada una de las mascotas individuales disponibles para adopción en el refugio.
    """
    STATUS_CHOICES = [
        ('AVAILABLE', 'Disponible'),
        ('PENDING', 'En Proceso'),
        ('ADOPTED', 'Adoptado'),
    ]

    name = models.CharField(max_length=100, verbose_name="Nombre")
    
    # Relación de Clave Foránea: Muchas mascotas pertenecen a una especie.
    # models.PROTECT evita que se elimine una especie si tiene mascotas asociadas.
    species = models.ForeignKey(
        Species, 
        on_delete=models.PROTECT, 
        related_name='pets', 
        verbose_name="Especie"
    )
    
    breed = models.CharField(max_length=100, default="Mestizo", verbose_name="Raza")
    
    # MinValueValidator(0) evita que por error se ingresen meses negativos.
    age_months = models.IntegerField(
        validators=[MinValueValidator(0)], 
        verbose_name="Edad (meses)"
    )
    
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    # Requiere que la librería Pillow esté instalada (pip install Pillow)
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
        # Muestra primero las mascotas más recientemente añadidas al refugio
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.species.name})"


class AdoptionApplication(models.Model):
    """
    Representa la postulación de un adoptante interesado en una mascota específica.
    """
    STATUS_CHOICES = [
        ('REVIEW', 'En Revisión'),
        ('APPROVED', 'Aprobada'),
        ('REJECTED', 'Rechazada'),
    ]

    # Relación de Clave Foránea: Una mascota puede recibir múltiples solicitudes.
    # models.CASCADE elimina las solicitudes automáticamente si la mascota es borrada.
    pet = models.ForeignKey(
        Pet, 
        on_delete=models.CASCADE, 
        related_name='applications', 
        verbose_name="Mascota"
    )
    
    applicant_name = models.CharField(max_length=150, verbose_name="Nombre del Solicitante")
    applicant_email = models.EmailField(verbose_name="Correo Electrónico")
    applicant_phone = models.CharField(max_length=20, verbose_name="Teléfono de Contacto")
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
        return f"Solicitud de {self.applicant_name} para {self.pet.name}"