from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework import filters

from ri_project import settings
from .models import Contacto, Departamento, Message
from .models import Usuarios
from .models import Producto
from .models import Servicio
from .models import Requisicion
from .models import Proveedor
from .models import OrdenDeCompra
from .models import Recibo
from .models import Project
from .serializer import ContactoSerializer, DepartamentoSerializer
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

import os
from django.http import FileResponse
from datetime import datetime
from xhtml2pdf import pisa
from io import BytesIO
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf.util import ErrorMsg
from pathlib import Path
import getpass

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

class ContactoViewSet(viewsets.ModelViewSet):
    queryset = Contacto.objects.all()
    serializer_class = ContactoSerializer
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
        proyecto_nombre = self.request.query_params.get('proyecto', None) # type: ignore

        if departamento_nombre is not None:
            queryset = queryset.filter(usuario__departamento__nombre=departamento_nombre)
            queryset = queryset.filter(Q(proyecto__isnull=True) | Q(proyecto__nombre=''))
            
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

        if proyecto_nombre is not None:
            queryset = queryset.filter(proyecto__nombre=proyecto_nombre)

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
        archivo_pdf = self.request.data.get('archivo_pdf', None) # type: ignore
        if archivo_pdf is not None:
            serializer.save(archivo_pdf=archivo_pdf)
        else:
            serializer.save()

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

    @action(detail=False, methods=['get'])
    def exportar(self, request):
        try:
            # Lee los datos JSON de la petición
            data = request.data

            # Variables que deseas inyectar en el HTML
            variables = data  # Usamos los datos JSON directamente

            # Directorio donde se encuentra la carpeta 'pdfs' en la raíz
            base_pdf_dir = os.path.join(settings.BASE_DIR, 'pdfs')

            # Obtén el nombre de usuario actual
            nombre_usuario = getpass.getuser()

            # Directorio para el usuario
            user_pdf_dir = os.path.join(base_pdf_dir, nombre_usuario)

            # Crea el directorio si no existe
            os.makedirs(user_pdf_dir, exist_ok=True)

            # Crea el nombre del archivo PDF
            pdf_file_name = f'{datetime.now().day}_{datetime.now().month}_{datetime.now().year}.pdf'

            # Ruta completa del archivo PDF
            pdf_file_path = os.path.join(user_pdf_dir, pdf_file_name)

            # Directorio relativo para el archivo PDF (usado para el enlace)
            pdf_relative_path = os.path.join(nombre_usuario, pdf_file_name)

            # Directorio completo para el archivo PDF
            pdf_full_path = os.path.join(settings.MEDIA_ROOT, pdf_relative_path)

            # Directorio de medios para el enlace del servidor
            pdf_media_url = os.path.join(settings.MEDIA_URL, pdf_relative_path)

            # Carga el entorno de Jinja2
            env = Environment(loader=FileSystemLoader('./'))
            template = env.get_template('miTabla.html')

            # Renderiza el HTML con las variables
            html_content = template.render(variables=variables)

            # Crea un objeto BytesIO para almacenar el PDF generado
            pdf_buffer = BytesIO()

            # Convierte el HTML en un archivo PDF
            pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)

            if pisa_status.err: # type: ignore
                print("Error al generar el PDF")
            else:
                # Guarda el PDF en la carpeta de medios
                with open(pdf_full_path, 'wb') as pdf_file:
                    pdf_file.write(pdf_buffer.getvalue())

                # Devuelve el enlace del servidor para visualizar el PDF
                return Response({'pdf_link': pdf_media_url})

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
