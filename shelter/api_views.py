import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import Pet, Species, Race, AdoptionApplication

"""
ENDPOINTS PARA MAESTROS: ESPECIES Y RAZAS
"""

class SpeciesListAPIView(View):
    """
    Lista todas las especies disponibles en el refugio (ej: Perro, Gato)
    """

    def get(self, request, *args, **kwargs):
        species = Species.objects.all()
        data = [{'id': s.id, 'name': s.name} for s in species]
        return JsonResponse({'species': data}, status=200)


class RaceListAPIView(View):
    """
    Lista las razas. Permite filtrar opcionalmente por especie (?species_id=1)
    """

    def get(self, request, *args, **kwargs):
        species_id = request.GET.get('species_id')
        races = Race.objects.all()
        if species_id:
            races = races.filter(species_id=species_id)
            
        data = [{'id': r.id, 'name': r.name, 'species_id': r.species_id} for r in races]
        return JsonResponse({'races': data}, status=200)


"""
ENDPOINTS PARA MASCOTAS
"""

@method_decorator(csrf_exempt, name='dispatch')
class PetListCreateAPIView(View):
    """
    Maneja el listado global de mascotas (GET) y la creación de nuevas (POST)
    """
    
    def get(self, request, *args, **kwargs):
        species_filter = request.GET.get('species')
        status_filter = request.GET.get('status')
        
        pets = Pet.objects.all()
        if species_filter:
            pets = pets.filter(species__name__iexact=species_filter)
        if status_filter:
            pets = pets.filter(status=status_filter)
            
        pets_data = []
        for pet in pets:
            pets_data.append({
                'id': pet.id,
                'name': pet.name,
                'species': pet.species.name,
                'race': pet.race.name if pet.race else 'Mestizo',
                'age_months': pet.age_months,
                'description': pet.description,
                'image': pet.image.url if pet.image else None,
                'status': pet.get_status_display()
            })
        return JsonResponse({'pets': pets_data}, status=200)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not getattr(request.user, 'is_shelter_admin', False):
            return JsonResponse({'error': 'No autorizado. Se requieren permisos de administrador.'}, status=403)
            
        try:
            data = json.loads(request.body)
            species = Species.objects.get(id=data['species_id'])
            race = Race.objects.get(id=data['race_id']) if data.get('race_id') else None
            
            pet = Pet.objects.create(
                name=data['name'],
                species=species,
                race=race,
                age_months=data['age_months'],
                description=data.get('description', ''),
                status=data.get('status', 'AVAILABLE')
            )
            return JsonResponse({'message': 'Mascota creada con éxito', 'pet_id': pet.id}, status=201)
        except (Species.DoesNotExist, Race.DoesNotExist):
            return JsonResponse({'error': 'La especie o raza proporcionada no existe'}, status=400)
        except KeyError as e:
            return JsonResponse({'error': f'El campo {str(e)} es obligatorio'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class PetDetailAPIView(View):
    """
    Maneja las operaciones individuales de una mascota: Ver (GET), Editar (PUT), Eliminar (DELETE)
    """
    
    def get(self, request, pk, *args, **kwargs):
        try:
            pet = Pet.objects.get(pk=pk)
            return JsonResponse({
                'id': pet.id,
                'name': pet.name,
                'species': pet.species.name,
                'race': pet.race.name if pet.race else 'Mestizo',
                'age_months': pet.age_months,
                'description': pet.description,
                'image': pet.image.url if pet.image else None,
                'status': pet.status
            }, status=200)
        except Pet.DoesNotExist:
            return JsonResponse({'error': 'Mascota no encontrada'}, status=404)

    def put(self, request, pk, *args, **kwargs):
        if not request.user.is_authenticated or not getattr(request.user, 'is_shelter_admin', False):
            return JsonResponse({'error': 'No autorizado'}, status=403)
            
        try:
            pet = Pet.objects.get(pk=pk)
            data = json.loads(request.body)
            
            pet.name = data.get('name', pet.name)
            pet.age_months = data.get('age_months', pet.age_months)
            pet.description = data.get('description', pet.description)
            pet.status = data.get('status', pet.status)
            
            if 'species_id' in data:
                pet.species = Species.objects.get(id=data['species_id'])
            if 'race_id' in data:
                pet.race = Race.objects.get(id=data['race_id']) if data['race_id'] else None
                
            pet.save()
            return JsonResponse({'message': 'Mascota actualizada con éxito'}, status=200)
        except Pet.DoesNotExist:
            return JsonResponse({'error': 'Mascota no encontrada'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)

    def delete(self, request, pk, *args, **kwargs):
        if not request.user.is_authenticated or not getattr(request.user, 'is_shelter_admin', False):
            return JsonResponse({'error': 'No autorizado'}, status=403)
            
        try:
            pet = Pet.objects.get(pk=pk)
            pet.delete()
            return JsonResponse({'message': 'Mascota eliminada del registro correctamente'}, status=200)
        except Pet.DoesNotExist:
            return JsonResponse({'error': 'Mascota no encontrada'}, status=404)


"""
ENDPOINTS PARA SOLICITUDES DE ADOPCIÓN
"""

@method_decorator(csrf_exempt, name='dispatch')
class AdoptionApplicationAPIView(View):
    """
    Maneja el envío de solicitudes (POST) y el listado de ellas para el Admin (GET)
    """
    
    def get(self, request, *args, **kwargs):
        """
        Lista todas las solicitudes de adopción recibidas (Solo Administradores)
        """

        if not request.user.is_authenticated or not getattr(request.user, 'is_shelter_admin', False):
            return JsonResponse({'error': 'Acceso denegado.'}, status=403)
            
        apps = AdoptionApplication.objects.all()
        data = []
        for a in apps:
            data.append({
                'id': a.id,
                'pet': {'id': a.pet.id, 'name': a.pet.name},
                'applicant': {'username': a.user.username, 'email': a.user.email, 'phone': a.user.phone},
                'motivation': a.motivation,
                'status': a.status,
                'created_at': a.created_at
            })
        return JsonResponse({'applications': data}, status=200)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Debes iniciar sesión para postular a una adopción.'}, status=401)
            
        try:
            data = json.loads(request.body)
            pet = Pet.objects.get(id=data['pet_id'])
            
            if pet.status == 'ADOPTED':
                return JsonResponse({'error': 'Esta mascota ya ha sido adoptada.'}, status=400)
                
            application = AdoptionApplication.objects.create(
                pet=pet,
                user=request.user,
                motivation=data['motivation']
            )

            pet.status = 'PENDING'
            pet.save()
            
            return JsonResponse({'message': 'Solicitud enviada con éxito.', 'application_id': application.id}, status=201)
            
        except Pet.DoesNotExist:
            return JsonResponse({'error': 'La mascota especificada no existe'}, status=404)
        except KeyError as e:
            return JsonResponse({'error': f'El campo {str(e)} es requerido'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class ApplicationReviewAPIView(View):
    """
    Permite al Admin aprobar o rechazar una solicitud y automatiza el estado de la mascota
    """
    
    def put(self, request, pk, *args, **kwargs):
        if not request.user.is_authenticated or not getattr(request.user, 'is_shelter_admin', False):
            return JsonResponse({'error': 'No autorizado.'}, status=403)
            
        try:
            data = json.loads(request.body)
            new_status = data['status']
            
            if new_status not in ['APPROVED', 'REJECTED']:
                return JsonResponse({'error': "Estado inválido. Debe ser 'APPROVED' o 'REJECTED'"}, status=400)

            with transaction.atomic():
                application = AdoptionApplication.objects.select_for_update().get(pk=pk)
                pet = application.pet
                
                application.status = new_status
                application.save()
                
                if new_status == 'APPROVED':
                    pet.status = 'ADOPTED'
                elif new_status == 'REJECTED':
                    has_other_pendings = AdoptionApplication.objects.filter(pet=pet, status='REVIEW').exclude(id=application.id).exists()
                    pet.status = 'PENDING' if has_other_pendings else 'AVAILABLE'
                
                pet.save()
                
            return JsonResponse({'message': f'Solicitud actualizada a {new_status} con éxito y estado de la mascota sincronizado.'}, status=200)
            
        except AdoptionApplication.DoesNotExist:
            return JsonResponse({'error': 'Solicitud de adopción no encontrada'}, status=404)
        except KeyError:
            return JsonResponse({'error': "El campo 'status' es obligatorio en el JSON body"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)