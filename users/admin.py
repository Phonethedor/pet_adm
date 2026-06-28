from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Role, CustomUser

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Permite al administrador gestionar los roles del sistema"""
    list_display = ('code', 'name', 'created_at')
    search_fields = ('code', 'name')


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Administrador personalizado para CustomUser. 
    Hereda de UserAdmin para mantener la gestión segura de contraseñas (bcrypt) y permisos.
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    ordering = ('username',)

    fieldsets = UserAdmin.fieldsets + (
        ('Información del Refugio y Contacto', {
            'fields': ('role', 'phone', 'address'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información del Refugio y Contacto', {
            'fields': ('role', 'phone', 'address'),
        }),
    )