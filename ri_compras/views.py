from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import filters
from .models import Departamento
from .models import Usuarios
from .models import Producto
from .models import Servicio
from .models import Requisicion
from .models import Proveedor
from .models import OrdenDeCompra
from .models import Recibo
from .models import Project
from .serializer import DepartamentoSerializer
from .serializer import UsuariosSerializer
from .serializer import ProductoSerializer
from .serializer import ServicioSerializer
from .serializer import RequisicionSerializer
from .serializer import ProveedorSerializer
from .serializer import OrdenDeCompraSerializer
from .serializer import ReciboSerializer
from .serializer import ProjectSerializer

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.views import APIView

class CustomObtainAuthToken(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            # Serializa el objeto de usuario
            user_serializer = UsuariosSerializer(user)
            return Response({'token': token.key, 'user': user_serializer.data})
        else:
            return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_400_BAD_REQUEST)

class GetUserFromToken(APIView):
    def get(self, request, *args, **kwargs):
        token_header = request.META.get('HTTP_AUTHORIZATION')
        if token_header is not None:
            try:
                # El encabezado de autorización generalmente tiene el formato 'Token abc123'
                # Así que necesitamos dividirlo para obtener el token real
                token_key = token_header.split(' ')[1]
                token = Token.objects.get(key=token_key)
                user = token.user
                user_serializer = UsuariosSerializer(user)
                return Response({'user': user_serializer.data})
            except (Token.DoesNotExist, IndexError):
                return Response({'error': 'Token inválido'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'No se proporcionó ningún token'}, status=status.HTTP_400_BAD_REQUEST)

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    search_fields =['project__nombre']
    ordering_fields = ['nombre']

class DepartamentoViewSet(viewsets.ModelViewSet):
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class UsuariosViewSet(viewsets.ModelViewSet):
    queryset = Usuarios.objects.all()
    serializer_class = UsuariosSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['departamento__nombre']
    ordering_fields = ['username']

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    ordering_fields = ['nombre']
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer
    ordering_fields = ['nombre']
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class RequisicionViewSet(viewsets.ModelViewSet):
    queryset = Requisicion.objects.all()
    serializer_class = RequisicionSerializer
    ordering_fields = ['fecha_creacion', 'aprobado', 'usuario']
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
class OrdenDeCompraViewSet(viewsets.ModelViewSet):
    queryset = OrdenDeCompra.objects.all()
    serializer_class = OrdenDeCompraSerializer
    ordering_fields = ['fecha_emision', 'total', 'usuario']
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
class ReciboViewSet(viewsets.ModelViewSet):
    queryset = Recibo.objects.all()
    serializer_class = ReciboSerializer
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]