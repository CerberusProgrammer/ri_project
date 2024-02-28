from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework import filters

from ri_project import settings
from .models import Contacto, Departamento, Message, Pedido, ProductoAlmacen
from .models import Usuarios
from .models import Producto
from .models import Servicio
from .models import Requisicion
from .models import Proveedor
from .models import OrdenDeCompra
from .models import Recibo
from .models import Project
from .serializer import ContactoSerializer, DepartamentoSerializer, PedidoSerializer, ProductoAlmacenSerializer
from .serializer import MessageSerializer
from .serializer import UsuariosSerializer
from .serializer import ProductoSerializer
from .serializer import ServicioSerializer
from .serializer import RequisicionSerializer
from .serializer import ProveedorSerializer
from .serializer import OrdenDeCompraSerializer
from .serializer import ReciboSerializer
from .serializer import ProjectSerializer
from .serializer import ProductoRequisicionSerializer

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
    queryset = Project.objects.all().order_by('-id')
    serializer_class = ProjectSerializer
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    ordering_fields = ['nombre']
    
    def list(self, request, *args, **kwargs):
        username = request.query_params.get('search', None)
        if username is not None:
            self.queryset = self.queryset.filter(usuario__username=username)
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def requisiciones_proyecto(self, request, id_proyecto=None):
        if id_proyecto is not None:
            requisiciones = Requisicion.objects.filter(proyecto__id=id_proyecto).order_by('-id')
            serializer = self.get_serializer(requisiciones, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No se proporcionó un ID de proyecto."})
    
    @action(detail=False, methods=['get'])
    def requisiciones_pendientes_proyecto(self, request, id_proyecto=None):
        if id_proyecto is not None:
            requisiciones = Requisicion.objects.filter(proyecto__id=id_proyecto, aprobado='PENDIENTE').order_by('-id')
            serializer = self.get_serializer(requisiciones, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No se proporcionó un ID de proyecto."})

    @action(detail=False, methods=['get'])
    def requisiciones_rechazadas_proyecto(self, request, id_proyecto=None):
        if id_proyecto is not None:
            requisiciones = Requisicion.objects.filter(proyecto__id=id_proyecto, aprobado='RECHAZADO').order_by('-id')
            serializer = self.get_serializer(requisiciones, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No se proporcionó un ID de proyecto."})

    @action(detail=False, methods=['get'])
    def requisiciones_aprobadas_proyecto(self, request, id_proyecto=None):
        if id_proyecto is not None:
            requisiciones = Requisicion.objects.filter(proyecto__id=id_proyecto, aprobado='APROBADO').order_by('-id')
            serializer = self.get_serializer(requisiciones, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No se proporcionó un ID de proyecto."})

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
    
    @action(detail=False, methods=['get'])
    def requisiciones_pendientes_departamento(self, request, id_departamento=None):
        if id_departamento is not None:
            requisiciones = Requisicion.objects.filter(usuario__departamento__id=id_departamento, aprobado='PENDIENTE').order_by('-id')
            serializer = RequisicionSerializer(requisiciones, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No se proporcionó un ID de departamento."})

    @action(detail=False, methods=['get'])
    def requisiciones_rechazadas_departamento(self, request, id_departamento=None):
        if id_departamento is not None:
            requisiciones = Requisicion.objects.filter(usuario__departamento__id=id_departamento, aprobado='RECHAZADO').order_by('-id')
            serializer = RequisicionSerializer(requisiciones, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No se proporcionó un ID de departamento."})

    @action(detail=False, methods=['get'])
    def requisiciones_aprobadas_departamento(self, request, id_departamento=None):
        if id_departamento is not None:
            requisiciones = Requisicion.objects.filter(usuario__departamento__id=id_departamento, aprobado='APROBADO').order_by('-id')
            serializer = RequisicionSerializer(requisiciones, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No se proporcionó un ID de departamento."})

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    ordering_fields = ['nombre']

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def ultimos(self, request):
        ultimos_productos = Producto.objects.order_by('-id')[:10]
        serializer = self.get_serializer(ultimos_productos, many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        queryset = Producto.objects.all()
        search = self.request.query_params.get('search', None) # type: ignore
        if search is not None:
            queryset = queryset.filter(Q(nombre__icontains=search) | Q(identificador__icontains=search))
        return queryset

class ProductoAlmacenViewSet(viewsets.ModelViewSet):
    queryset = ProductoAlmacen.objects.all()
    serializer_class = ProductoAlmacenSerializer
    ordering_fields = ['nombre']

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        identificador = self.request.query_params.get('identificador', None)
        nombre = self.request.query_params.get('nombre', None)
        cantidad = self.request.query_params.get('cantidad', None)
        id = self.request.query_params.get('id', None)

        if identificador is not None:
            queryset = queryset.filter(identificador=identificador)
        
        if nombre is not None:
            queryset = queryset.filter(nombre__icontains=nombre)
        
        if cantidad is not None:
            queryset = queryset.filter(cantidad=cantidad)
        
        if id is not None:
            queryset = queryset.filter(id=id)

        return queryset

class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer
    ordering_fields = ['nombre']
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def ultimos(self, request):
        ultimos_servicios = Servicio.objects.order_by('-id')[:10]
        serializer = self.get_serializer(ultimos_servicios, many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        queryset = Servicio.objects.all()
        search = self.request.query_params.get('search', None) # type: ignore
        if search is not None:
            queryset = queryset.filter(Q(nombre__icontains=search))
        return queryset

class ContactoViewSet(viewsets.ModelViewSet):
    queryset = Contacto.objects.all().order_by('-id')
    serializer_class = ContactoSerializer
    ordering_fields = ['nombre']
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class RequisicionViewSet(viewsets.ModelViewSet):
    queryset = Requisicion.objects.all().order_by('-id')
    serializer_class = RequisicionSerializer
    ordering_fields = ['fecha_creacion', 'aprobado', 'usuario']
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def ultimas_requisiciones(self, request, pk=None):
        if pk is not None:
            ultimas_requisiciones = Requisicion.objects.filter(usuario__id=pk).order_by('-id')[:10]
            serializer = self.get_serializer(ultimas_requisiciones, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No se proporcionó un ID de usuario."})

    @action(detail=True, methods=['get'])
    def requisiciones_rechazadas(self, request, pk=None):
        if pk is not None:
            requisiciones = Requisicion.objects.filter(usuario__id=pk, aprobado='RECHAZADO').order_by('-id')[:10]
            serializer = self.get_serializer(requisiciones, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No se proporcionó un ID de usuario."})

    @action(detail=True, methods=['get'])
    def requisiciones_aprobadas(self, request, pk=None):
        if pk is not None:
            requisiciones = Requisicion.objects.filter(usuario__id=pk, aprobado='APROBADO').order_by('-id')[:10]
            serializer = self.get_serializer(requisiciones, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No se proporcionó un ID de usuario."})

    @action(detail=True, methods=['post'])
    def requisiciones_departamento(self, request, pk=None):
        if pk is not None:
            requisiciones = Requisicion.objects.filter(usuario__id=pk, proyecto__isnull=True).order_by('-id')[:10]
            serializer = self.get_serializer(requisiciones, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No se proporcionó un ID de usuario."})

    @action(detail=True, methods=['post'])
    def requisiciones_proyecto(self, request, pk=None):
        if pk is not None:
            requisiciones = Requisicion.objects.filter(usuario__id=pk, proyecto__isnull=False).order_by('-id')[:10]
            serializer = self.get_serializer(requisiciones, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No se proporcionó un ID de usuario."})
        
    @action(detail=True, methods=['get'])
    def requisiciones_pendientes(self, request, pk=None):
        if pk is not None:
            requisiciones = Requisicion.objects.filter(usuario__id=pk, aprobado='PENDIENTE').order_by('-id')[:10]
            serializer = self.get_serializer(requisiciones, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No se proporcionó un ID de usuario."})
    
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
            aprobado = aprobado.upper()  # Convertir a mayúsculas para coincidir con tus opciones
            if aprobado in dict(Requisicion.ESTADO_APROBACION).keys():
                queryset = queryset.filter(aprobado=aprobado)
            
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
    queryset = Proveedor.objects.all().order_by('-id')
    serializer_class = ProveedorSerializer
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Proveedor.objects.all()
        search = self.request.query_params.get('search', None) # type: ignore
        if search is not None:
            queryset = queryset.filter(Q(nombre__icontains=search))
        return queryset

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all().order_by('-id')
    serializer_class = PedidoSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class OrdenDeCompraViewSet(viewsets.ModelViewSet):
    queryset = OrdenDeCompra.objects.all().order_by('-id')
    serializer_class = OrdenDeCompraSerializer
    ordering_fields = ['fecha_emision', 'total', 'usuario', 'id']
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        id = self.request.query_params.get('id', None)
        fecha_inicio = self.request.query_params.get('fecha_inicio', None)
        fecha_fin = self.request.query_params.get('fecha_fin', None)
        orden_recibida = self.request.query_params.get('orden', None)
        proveedor_nombre = self.request.query_params.get('proveedor', None)
        requisicion_id = self.request.query_params.get('requisicion', None)
        usuario_username = self.request.query_params.get('usuario', None)
        estado = self.request.query_params.get('estado', None)
        recibido = self.request.query_params.get('recibido', None)

        if id is not None:
            queryset = queryset.filter(id=id)
        
        if fecha_inicio is not None and fecha_fin is not None:
            fecha_inicio = parse_date(fecha_inicio)
            fecha_fin = parse_date(fecha_fin)
            queryset = queryset.filter(Q(fecha_entrega__range=[fecha_inicio, fecha_fin]) | Q(fecha_entrega__isnull=True))
        elif fecha_inicio is not None:
            fecha_inicio = parse_date(fecha_inicio)
            queryset = queryset.filter(Q(fecha_entrega__gte=fecha_inicio) | Q(fecha_entrega__isnull=True))
        elif fecha_fin is not None:
            fecha_fin = parse_date(fecha_fin)
            queryset = queryset.filter(Q(fecha_entrega__lte=fecha_fin) | Q(fecha_entrega__isnull=True))

        if orden_recibida is not None:
            orden_recibida = orden_recibida.lower() in ['true', '1']
            queryset = queryset.filter(orden_recibida=orden_recibida)

        if proveedor_nombre is not None:
            queryset = queryset.filter(proveedor__nombre=proveedor_nombre)

        if requisicion_id is not None:
            queryset = queryset.filter(requisicion__id=requisicion_id)

        if usuario_username is not None:
            queryset = queryset.filter(usuario__username=usuario_username)

        if estado is not None:
            queryset = queryset.filter(estado=estado)
            
        if recibido is not None:
            queryset = queryset.filter(orden_recibida=recibido)

        return queryset

    
    @action(detail=True, methods=['post'])
    def actualizar_productos_recibidos(self, request, pk=None):
        orden = self.get_object()
        productos_data = request.data

        cantidad_total_recibida = 0
        for producto_data in productos_data:
            id_producto = producto_data.get('id')
            cantidad_recibida = producto_data.get('cantidad_recibida')

            cantidad_total_recibida += cantidad_recibida

            producto_requisicion = get_object_or_404(orden.requisicion.productos, id=id_producto)

            # Actualizar la cantidad recibida del ProductoRequisicion
            producto_requisicion.cantidad_recibida += cantidad_recibida
            producto_requisicion.save()

            # Buscar el ProductoAlmacen existente o crear uno nuevo
            producto_almacen, created = ProductoAlmacen.objects.get_or_create(
                orden_compra=orden,
                nombre=producto_requisicion.nombre,
                defaults={
                    'identificador': producto_requisicion.identificador,
                    'descripcion': producto_requisicion.descripcion,
                    'costo': producto_requisicion.costo,
                    'cantidad': 0
                }
            )

            # Actualizar la cantidad del ProductoAlmacen
            producto_almacen.cantidad += cantidad_recibida
            producto_almacen.save()

        cantidad_total_orden = sum([producto.cantidad for producto in orden.requisicion.productos.all()])

        if cantidad_total_recibida >= cantidad_total_orden:
            orden.orden_recibida = True
            orden.estado = "EN ALMACEN"
            orden.save()

        orden = self.get_object()

        serializer = self.get_serializer(orden)
        return Response(serializer.data)


    @action(detail=False, methods=['post'])
    def exportar(self, request):
        try:
            data = request.data
            variables = data

            subtotal = 0
            for i in range(len(data['requisicion_detail']['productos'])):
                costo = float(data['requisicion_detail']['productos'][i]['costo']) * float(data['requisicion_detail']['productos'][i]['cantidad'])
                subtotal += costo
                variables['requisicion_detail']['productos'][i]['costo_total'] = format(costo, ',.6f')

            for i in range(len(data['requisicion_detail']['servicios'])):
                subtotal += float(data['requisicion_detail']['servicios'][i]['costo'])

            iva_value = variables['proveedor_detail']['iva']
            iva = subtotal * float(iva_value) if iva_value is not None else 0.0

            iva_retenido_value = variables['proveedor_detail']['iva_retenido']
            iva_retenido = subtotal * float(iva_retenido_value) if iva_retenido_value is not None else 0.0

            isr_retenido_value = variables['proveedor_detail']['isr_retenido']
            isr_retenido = subtotal * float(isr_retenido_value) if isr_retenido_value is not None else 0.0

            total = subtotal + iva + isr_retenido + iva_retenido

            variables['subtotal'] = format(subtotal, ',.6f')
            variables['iva'] = format(iva, ',.6f')
            variables['isr_retenido'] = format(isr_retenido, ',.6f')
            variables['iva_retenido'] = format(iva_retenido, ',.6f')
            variables['total'] = format(total, ',.6f')

            credito_value = variables['proveedor_detail']['credito']
            variables['hay_credito'] = "Credito disponible" if credito_value is not None and float(credito_value) > 0 else "Sin credito disponible"

            if not variables['requisicion_detail']['productos']:
                variables['divisa'] = variables['requisicion_detail']['servicios'][0]['divisa']

            if not variables['requisicion_detail']['servicios']:
                variables['divisa'] = variables['requisicion_detail']['productos'][0]['divisa']

            username = data.get("usuario_detail", {}).get("username")
            username = username.lower().replace(' ', '_')
            id = variables['id']
            variables['usuario_detail']['username'] = username

            pdf_file_name = f'OC_{id}_{username}.pdf'

            pdf_relative_path = os.path.join('pdfs', pdf_file_name)
            pdf_full_path = os.path.join(settings.MEDIA_ROOT, pdf_relative_path)
            pdf_media_url = os.path.join(settings.MEDIA_URL, pdf_relative_path)

            template_dir = os.path.join(settings.BASE_DIR, 'ri_compras', 'templates')
            env = Environment(loader=FileSystemLoader(template_dir))
            template = env.get_template('miTabla.html')

            html_content = template.render(variables=variables)

            pdf_buffer = BytesIO()
            pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)

            if pisa_status.err:  # type: ignore
                print("Error al generar el PDF")
            else:
                with open(pdf_full_path, 'wb') as pdf_file:
                    pdf_file.write(pdf_buffer.getvalue())

                return Response({'pdf_link': pdf_media_url})

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ReciboViewSet(viewsets.ModelViewSet):
    queryset = Recibo.objects.all()
    serializer_class = ReciboSerializer
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by('-id')
    serializer_class = MessageSerializer
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username']

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
