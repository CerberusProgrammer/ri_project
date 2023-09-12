import random
import string
from django.http import JsonResponse
from .models import Usuarios
from django.utils import timezone

def crear_usuario(request):
    if request.method == 'POST':
        data = request.POST  # O utiliza request.body para obtener datos JSON

        # Verificar si ya existe un usuario con el mismo username
        username = data.get('username')
        if Usuarios.objects.filter(username=username).exists():
            return JsonResponse({'error': 'El username ya está en uso'}, status=400)

        # Verificar si ya existe un usuario con el mismo correo
        correo = data.get('correo')
        if Usuarios.objects.filter(correo=correo).exists():
            return JsonResponse({'error': 'El correo ya está en uso'}, status=400)

        # Verificar si el rol es válido (coincide con los roles disponibles)
        rol = data.get('rol')
        roles_disponibles = [choice[0] for choice in Usuarios.PUESTOS]
        if rol not in roles_disponibles:
            return JsonResponse({'error': 'El rol no es válido'}, status=400)

        # Generar un token aleatorio
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=50))

        # Crear un nuevo usuario
        usuario = Usuarios(
            token=token,
            joined_at=timezone.now(),
            is_active=True,
            username=username,
            nombre=data.get('nombre'),
            telefono=data.get('telefono'),
            correo=correo,
            rol=rol
        )
        usuario.save()

        # Crear una respuesta JSON con los datos del usuario creado
        response_data = {
            'id': usuario.id,
            'token': usuario.token,
            'joined_at': usuario.joined_at,
            'is_active': usuario.is_active,
            'username': usuario.username,
            'nombre': usuario.nombre,
            'telefono': usuario.telefono,
            'correo': usuario.correo,
            'rol': usuario.rol,
        }
        
        return JsonResponse(response_data, status=201)  # 201 Created
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
