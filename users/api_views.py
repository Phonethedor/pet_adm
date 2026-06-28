import json
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import IntegrityError
from .models import CustomUser, Role

@method_decorator(csrf_exempt, name='dispatch')
class SignUpAPIView(View):
    """
    Endpoint REST para registrar un nuevo adoptante
    """
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            
            try:
                adoptant_role = Role.objects.get(code='ADOPTANT')
            except Role.DoesNotExist:
                return JsonResponse({'error': 'El rol ADOPTANT no existe en la BD. Créalo primero en el panel de Admin.'}, status=500)

            user = CustomUser.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                role=adoptant_role,
                phone=data.get('phone', ''),
                address=data.get('address', '')
            )
            
            return JsonResponse({
                'message': 'Usuario registrado con éxito',
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'role': user.role.name
                }
            }, status=201)
            
        except KeyError as e:
            return JsonResponse({'error': f'El campo {str(e)} es obligatorio'}, status=400)
        except IntegrityError:
            return JsonResponse({'error': 'El nombre de usuario o email ya existe'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class LoginAPIView(View):
    """
    Endpoint REST para iniciar sesión
    """

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            username = data['username']
            password = data['password']
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return JsonResponse({
                        'message': 'Inicio de sesión exitoso',
                        'user': {
                            'username': user.username,
                            'role': user.role.name if user.role else 'Sin Rol',
                            'is_admin': user.is_shelter_admin
                        }
                    }, status=200)
                else:
                    return JsonResponse({'error': 'Esta cuenta está desactivada'}, status=403)
            else:
                return JsonResponse({'error': 'Credenciales inválidas'}, status=401)
                
        except KeyError:
            return JsonResponse({'error': 'Faltan campos obligatorios (username, password)'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutAPIView(View):
    """
    Endpoint REST para cerrar sesión
    """

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
            return JsonResponse({'message': 'Sesión cerrada con éxito'}, status=200)
        return JsonResponse({'error': 'No hay ninguna sesión activa'}, status=400)

class UserProfileAPIView(View):
    """ 
    Devuelve el perfil del usuario actualmente logueado mediante la cookie de sesión
    """

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'No has iniciado sesión'}, status=401)
            
        user = request.user
        return JsonResponse({
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'address': user.address,
            'role': user.role.name if user.role else 'Sin Rol',
            'is_admin': user.is_shelter_admin
        }, status=200)


class RoleListAPIView(View):
    """
    Lista los roles del sistema (Útil para desarrollo y depuración en Postman)
    """

    def get(self, request, *args, **kwargs):
        roles = Role.objects.all()
        roles_data = [{'id': r.id, 'code': r.code, 'name': r.name} for r in roles]
        return JsonResponse({'roles': roles_data}, status=200)


class UserListAPIView(View):
    """
    Lista todos los usuarios registrados en el sistema (PROTEGIDO: Solo el Admin puede ver esto)
    """

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not getattr(request.user, 'is_shelter_admin', False):
            return JsonResponse({'error': 'Acceso denegado. Se requieren permisos de administrador.'}, status=403)
            
        users = CustomUser.objects.all()
        users_data = []
        for u in users:
            users_data.append({
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'full_name': u.get_full_name(),
                'role': u.role.name if u.role else 'Sin Rol',
                'is_active': u.is_active
            })
        return JsonResponse({'users': users_data}, status=200)