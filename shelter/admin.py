from django.contrib import admin
from .models import Species, Race, Pet, AdoptionApplication

@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    """
    Permite gestionar las especies (ej: Perro, Gato)
    """

    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    """
    Permite gestionar las razas vinculándolas a una especie (ej: Labrador -> Perro)
    """

    list_display = ('name', 'species', 'created_at')
    list_filter = ('species',)
    search_fields = ('name', 'species__name')


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    """
    Gestiona el inventario de mascotas en el refugio
    """

    list_display = ('name', 'species', 'race', 'age_months', 'status', 'created_at')
    list_filter = ('species', 'status', 'race')
    search_fields = ('name', 'species__name', 'race__name')


@admin.register(AdoptionApplication)
class AdoptionApplicationAdmin(admin.ModelAdmin):
    """
    Gestiona el flujo de solicitudes de adopción recibidas
    """

    list_display = ('get_applicant_user', 'pet', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email', 'pet__name')

    def get_applicant_user(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_applicant_user.short_description = 'Solicitante'