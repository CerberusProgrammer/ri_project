from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework import filters
from .models import Departamento, Message
from .models import Usuarios
from .models import Producto
from .models import Servicio
from .models import Requisicion
from .models import Proveedor
from .models import OrdenDeCompra
from .models import Recibo
from .models import Project
from .serializer import DepartamentoSerializer
from .serializer import MessageSerializer
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
from django.db.models import Q
from django.http import FileResponse
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
    ordering_fields = ['nombre']
    
    def list(self, request, *args, **kwargs):
        username = request.query_params.get('search', None)
        if username is not None:
            self.queryset = self.queryset.filter(usuario__username=username)
        return super().list(request, *args, **kwargs)

class UsuariosViewSet(viewsets.ModelViewSet):
    queryset = Usuarios.objects.all()
    serializer_class = UsuariosSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['departamento__nombre']
    ordering_fields = ['username']

class DepartamentoViewSet(viewsets.ModelViewSet):
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

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
    
    def get_queryset(self):
        queryset = super().get_queryset()
        departamento_nombre = self.request.query_params.get('departamento', None) # type: ignore
        aprobado = self.request.query_params.get('aprobado', None) # type: ignore
        ordenado = self.request.query_params.get('ordenado', None) # type: ignore

        if departamento_nombre is not None:
            queryset = queryset.filter(usuario__departamento__nombre=departamento_nombre)
        
        if aprobado is not None:
            if aprobado.lower() == 'true':
                queryset = queryset.filter(aprobado=True)
            elif aprobado.lower() == 'false':
                queryset = queryset.filter(aprobado=False)
        
        if ordenado is not None:
            if ordenado.lower() == 'true':
                queryset = queryset.filter(ordenado=True)
            elif ordenado.lower() == 'false':
                queryset = queryset.filter(ordenado=False)

        # Agrega estas líneas para filtrar por proyecto nulo o vacío
        queryset = queryset.filter(Q(proyecto__isnull=True) | Q(proyecto__nombre=''))

        return queryset

    @action(detail=True, methods=['post'])
    def update_producto(self, request, pk=None):
        requisicion = self.get_object()
        producto_data = request.data.get('producto')

        producto = requisicion.productos.get(id=producto_data.get('id'))

        producto.nombre = producto_data.get('nombre', producto.nombre)
        producto.descripcion = producto_data.get('descripcion', producto.descripcion)
        producto.cantidad = producto_data.get('cantidad', producto.cantidad)
        producto.costo = producto_data.get('costo', producto.costo)
        producto.identificador = producto_data.get('identificador', producto.identificador)
        producto.divisa = producto_data.get('divisa', producto.divisa)

        producto.save()

        return Response({'status': 'Producto actualizado'})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(archivo_pdf=self.request.data.get('archivo_pdf')) # type: ignore

    @action(detail=True, methods=['get'])
    def descargar_pdf(self, request, pk=None):
        requisicion = self.get_object()
        if requisicion.archivo_pdf:
            return FileResponse(requisicion.archivo_pdf, as_attachment=True, filename='archivo.pdf')
        else:
            return Response({'error': 'No hay archivo PDF para esta requisición'}, status=404)

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

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username']

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

#@api_view(['POST'])
#def crear_orden_de_compra(request):
#    if request.method == 'POST':
#        serializer = OrdenDeCompraSerializer(data=request.data)
#        if serializer.is_valid():
#            orden_de_compra = serializer.save()
#
#            # Renderizar el HTML con los datos de la orden de compra
#            contexto = {'orden_de_compra': orden_de_compra}
#            html = render(request, 'detalle_orden_de_compra.html', contexto)
#
#            # Crear un archivo PDF vacío donde se escribirá la salida
#            response = HttpResponse(content_type='application/pdf')
#            response['Content-Disposition'] = f'attachment; filename="orden_de_compra_{orden_de_compra.id}.pdf"'
#
#            # Utilizar pisa para convertir el HTML a PDF y escribirlo en la respuesta
#            pisa.CreatePDF(html.content, dest=response)
#
#            return response
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)