from rest_framework import permissions

class IsAdminAndTokenMatches(permissions.BasePermission):
    def has_permission(self, request, view):
        # Verificar si el usuario tiene permisos de "ADMINISTRADOR"
        return request.user and request.user.rol == 'ADMINISTRADOR'

    def has_object_permission(self, request, view, obj):
        # Verificar si el token en el encabezado coincide con el usuario
        return request.auth and request.auth == obj.token
