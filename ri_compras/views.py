from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import UsuariosForm
import random
import string

def crear_usuario(request):
    if request.method == 'POST':
        form = UsuariosForm(request.POST)
        if form.is_valid():
            # Guardar el objeto Usuarios si el formulario es válido
            usuario = form.save()
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=50))

            # Crear una respuesta JSON con los datos del objeto usuario
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
            
            return JsonResponse(response_data)  # Devolver la respuesta JSON
    else:
        form = UsuariosForm()
    
    return render(request, 'crear_usuario.html', {'form': form})
