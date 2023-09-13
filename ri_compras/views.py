from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Usuarios
from django.db import IntegrityError
from django.contrib.auth.password_validation import validate_password
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

class UsuariosViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        nombre = request.data.get('nombre')
        telefono = request.data.get('telefono')
        correo = request.data.get('correo')
        rol = request.data.get('rol')
        
        if not all([username, password, nombre, telefono, correo, rol]):
            return Response({"error": "Todos los campos son requeridos"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            validate_password(password)
        except Exception as e:
            return Response({"Contraseña invalida": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = Usuarios.objects.create(
                username=username,
                nombre=nombre,
                telefono=telefono,
                correo=correo,
                rol=rol,
            )
        except IntegrityError as e:
            return Response({"error": "El correo o nombre de usuario ya están en uso"}, status=status.HTTP_400_BAD_REQUEST)

        # Asignar la contraseña cifrada al usuario
        user.set_password(password)
        user.save()

        # Crear un token para el usuario
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "username": username,
            "nombre": nombre,
            "telefono": telefono,
            "correo": correo,
            "rol": rol,
            "token": token.key
        }, status=status.HTTP_201_CREATED)
        
    @action(detail=False, methods=['GET'], authentication_classes=[TokenAuthentication], permission_classes=[IsAuthenticated])
    def details(self, request):
        user = request.user  # El usuario autenticado se almacena en request.user
        data = {
            "id": user.id,
            "joined_at": user.joined_at,
            "is_active": user.is_active,
            "username": user.username,
            "nombre": user.nombre,
            "telefono": user.telefono,
            "correo": user.correo,
            "rol": user.rol
        }
        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['PUT'], authentication_classes=[TokenAuthentication], permission_classes=[IsAuthenticated])
    def update_user(self, request):
        user = request.user  # Obtén el usuario autenticado a través del token

        # Realizar la actualización de los datos del usuario
        user.nombre = request.data.get('nombre', user.nombre)
        user.telefono = request.data.get('telefono', user.telefono)
        user.correo = request.data.get('correo', user.correo)
        user.rol = request.data.get('rol', user.rol)
        user.save()

        data = {
            "id": user.id,
            "joined_at": user.joined_at,
            "is_active": user.is_active,
            "username": user.username,
            "nombre": user.nombre,
            "telefono": user.telefono,
            "correo": user.correo,
            "rol": user.rol
        }
        return Response(data, status=status.HTTP_200_OK)
