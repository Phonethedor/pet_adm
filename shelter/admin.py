from django.contrib import admin
from .models import Species, Pet, AdoptionApplication

# Register your models here.

@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    # Cambiamos 'species' por 'species__name' en las búsquedas para acceder al texto del modelo relacionado
    list_display = ('name', 'species', 'breed', 'age_months', 'status', 'created_at')
    list_filter = ('species', 'status')
    search_fields = ('name', 'breed', 'species__name')

@admin.register(AdoptionApplication)
class AdoptionApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant_name', 'pet', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('applicant_name', 'applicant_email', 'pet__name')