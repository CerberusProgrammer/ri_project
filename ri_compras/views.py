from django.shortcuts import get_object_or_404
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework import filters
from django.db.models import CharField
from django.db.models.functions import Cast
from django.db.models import Count

from ri_project import settings
from .models import Contacto, Departamento, Estante, Message, Pedido, ProductoAlmacen, Rack
from .models import Usuarios
from .models import Producto
from .models import Servicio
from .models import Requisicion
from .models import Proveedor
from .models import OrdenDeCompra
from .models import Recibo
from .models import Project
from .serializer import ContactoSerializer, DepartamentoSerializer, EstanteSerializer, PedidoSerializer, ProductoAlmacenSerializer, RackSerializer
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
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, F, FloatField

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
    
    def get_queryset(self):
        queryset = Project.objects.all().order_by('-id')
        nombre = self.request.query_params.get('nombre', None)
        usuario = self.request.query_params.get('usuario', None)

        if nombre is not None:
            queryset = queryset.filter(nombre__icontains=nombre)
        if usuario is not None:
            queryset = queryset.filter(usuario__username=usuario)

        return queryset
    
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
    queryset = Producto.objects.all().order_by('-id')
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
        queryset = Producto.objects.all().order_by('-id')
        identificador = self.request.query_params.get('identificador', None)
        nombre = self.request.query_params.get('nombre', None)
        descripcion = self.request.query_params.get('descripcion', None)
        costo = self.request.query_params.get('costo', None)
        divisa = self.request.query_params.get('divisa', None)
        cantidad = self.request.query_params.get('cantidad', None)
        unidad_de_medida = self.request.query_params.get('medida', None)
        limit = self.request.query_params.get('limit', None)


        if identificador is not None:
            queryset = queryset.filter(identificador__icontains=identificador)

        if nombre is not None:
            queryset = queryset.filter(nombre__icontains=nombre)

        if descripcion is not None:
            queryset = queryset.filter(descripcion__icontains=descripcion)

        if costo is not None:
            if '>' in costo and '<' in costo:
                min_costo, max_costo = costo.split('<')
                min_costo = min_costo.replace('>', '')
                queryset = queryset.filter(costo__gt=min_costo, costo__lt=max_costo)
            elif '>' in costo:
                min_costo = costo.replace('>', '')
                queryset = queryset.filter(costo__gt=min_costo)
            elif '<' in costo:
                max_costo = costo.replace('<', '')
                queryset = queryset.filter(costo__lt=max_costo)
            else:
                queryset = queryset.filter(costo=costo)

        if divisa is not None:
            queryset = queryset.filter(divisa=divisa)

        if cantidad is not None:
            if '>' in cantidad and '<' in cantidad:
                min_cantidad, max_cantidad = cantidad.split('<')
                min_cantidad = min_cantidad.replace('>', '')
                queryset = queryset.filter(cantidad__gt=min_cantidad, cantidad__lt=max_cantidad)
            elif '>' in cantidad:
                min_cantidad = cantidad.replace('>', '')
                queryset = queryset.filter(cantidad__gt=min_cantidad)
            elif '<' in cantidad:
                max_cantidad = cantidad.replace('<', '')
                queryset = queryset.filter(cantidad__lt=max_cantidad)
            else:
                queryset = queryset.filter(cantidad=cantidad)

        if unidad_de_medida is not None:
            queryset = queryset.filter(unidad_de_medida__icontains=unidad_de_medida)
        
        if limit is not None:
            try:
                limit = int(limit)
                queryset = queryset[:limit]
            except ValueError:
                pass

        return queryset

class ProductoAlmacenViewSet(viewsets.ModelViewSet):
    queryset = ProductoAlmacen.objects.all().order_by('-id')
    serializer_class = ProductoAlmacenSerializer
    ordering_fields = ['nombre']

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        identificador = self.request.query_params.get('identificador', None)
        nombre = self.request.query_params.get('nombre', None)
        descripcion = self.request.query_params.get('descripcion', None)
        costo = self.request.query_params.get('costo', None)
        divisa = self.request.query_params.get('divisa', None)
        cantidad = self.request.query_params.get('cantidad', None)
        orden_compra_id = self.request.query_params.get('orden', None)
        posicion_id = self.request.query_params.get('posicion_id', None)
        id = self.request.query_params.get('id', None)
        rack_nombre = self.request.query_params.get('rack', None)
        estante_numero = self.request.query_params.get('estante', None)
        liberado = self.request.query_params.get('liberado', None)

        if rack_nombre is not None:
            queryset = queryset.filter(posicion__rack__nombre=rack_nombre)
            if estante_numero is not None:
                queryset = queryset.filter(posicion__numero=estante_numero)

        if identificador is not None:
            queryset = queryset.filter(identificador__icontains=identificador)
            
        if nombre is not None:
            queryset = queryset.filter(nombre__icontains=nombre)
            
        if descripcion is not None:
            queryset = queryset.filter(descripcion__icontains=descripcion)
            
        if costo is not None:
            if '>' in costo and '<' in costo:
                min_costo, max_costo = costo.split('<')
                min_costo = min_costo.replace('>', '')
                queryset = queryset.filter(costo__gt=min_costo, costo__lt=max_costo)
            elif '>' in costo:
                min_costo = costo.replace('>', '')
                queryset = queryset.filter(costo__gt=min_costo)
            elif '<' in costo:
                max_costo = costo.replace('<', '')
                queryset = queryset.filter(costo__lt=max_costo)
            else:
                queryset = queryset.filter(costo=costo)
            
        if divisa is not None:
            queryset = queryset.filter(divisa=divisa)
            
        if cantidad is not None:
            if '>' in cantidad and '<' in cantidad:
                min_cantidad, max_cantidad = cantidad.split('<')
                min_cantidad = min_cantidad.replace('>', '')
                queryset = queryset.filter(cantidad__gt=min_cantidad, cantidad__lt=max_cantidad)
            elif '>' in cantidad:
                min_cantidad = cantidad.replace('>', '')
                queryset = queryset.filter(cantidad__gt=min_cantidad)
            elif '<' in cantidad:
                max_cantidad = cantidad.replace('<', '')
                queryset = queryset.filter(cantidad__lt=max_cantidad)
            else:
                queryset = queryset.filter(cantidad=cantidad)
            
        if orden_compra_id is not None:
            queryset = queryset.filter(orden_compra__id=orden_compra_id)
            
        if posicion_id is not None:
            queryset = queryset.filter(posicion__id=posicion_id)
            
        if id is not None:
            queryset = queryset.filter(id=id)
        
        if liberado is not None:
            if liberado.lower() == 'true':
                queryset = queryset.filter(Q(orden_compra__isnull=True) | Q(orden_liberada=True))
            elif liberado.lower() == 'false':
                queryset = queryset.filter(Q(orden_compra__isnull=False) & Q(orden_liberada=False))

        return queryset

    @action(detail=True, methods=['get'])
    def obtener_pedidos(self, request, pk=None):
        producto = self.get_object()
        pedidos = producto.pedidos.all()

        serializer = PedidoSerializer(pedidos, many=True)

        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def obtener_inventariado(self, request):
        cantidad_total = ProductoAlmacen.objects.all().aggregate(Sum('cantidad'))['cantidad__sum']
        costo_total_pesos = ProductoAlmacen.objects.filter(divisa='MXN').aggregate(total=Sum(F('costo') * F('cantidad'), output_field=FloatField()))['total']
        costo_total_dolares = ProductoAlmacen.objects.filter(divisa='USD').aggregate(total=Sum(F('costo') * F('cantidad'), output_field=FloatField()))['total']
        pedido_total = Pedido.objects.all().aggregate(Sum('cantidad'))['cantidad__sum']

        usuarios_con_mas_pedidos = Pedido.objects.values('usuario_nombre').annotate(total_pedidos=Count('cantidad')).order_by('-total_pedidos')[:10]
        productos_mas_pedidos = Pedido.objects.values('producto_nombre').annotate(total_pedidos=Sum('cantidad')).order_by('-total_pedidos')[:10]
        fecha_con_mas_pedidos = Pedido.objects.extra({'fecha_pedido' : "date(fecha_pedido)"}).values('fecha_pedido').annotate(total_pedidos=Count('id')).order_by('-total_pedidos')[:10]
        cantidad_por_rack = ProductoAlmacen.objects.values('posicion__rack__nombre').annotate(total_productos=Sum('cantidad')).order_by('-total_productos')

        return Response({
            "cantidad_total": cantidad_total if cantidad_total else 0,
            "costo_total_pesos": costo_total_pesos if costo_total_pesos else 0.0,
            "costo_total_dolares": costo_total_dolares if costo_total_dolares else 0.0,
            "pedido_total": pedido_total if pedido_total else 0,
            "usuarios_con_mas_pedidos": usuarios_con_mas_pedidos,
            "productos_mas_pedidos": productos_mas_pedidos,
            "fecha_con_mas_pedidos": fecha_con_mas_pedidos,
            "cantidad_por_rack": cantidad_por_rack,
        })

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
    
    def get_queryset(self):
        queryset = super().get_queryset()
        departamento_nombre = self.request.query_params.get('departamento', None)
        aprobado = self.request.query_params.get('aprobado', None)
        ordenado = self.request.query_params.get('ordenado', None)
        proyecto_nombre = self.request.query_params.get('proyecto', None)
        fecha_creacion = self.request.query_params.get('fecha_creacion', None)
        fecha_aprobado = self.request.query_params.get('fecha_aprobado', None)
        fecha_entrega_estimada = self.request.query_params.get('fecha_entrega_estimada', None)
        fecha_ordenado = self.request.query_params.get('fecha_ordenado', None)
        motivo = self.request.query_params.get('motivo', None)
        total = self.request.query_params.get('total', None)
        usuario_id = self.request.query_params.get('usuario', None)
        proveedor_id = self.request.query_params.get('proveedor', None)
        tipo_de_cambio = self.request.query_params.get('tipo_de_cambio', None)
        
        if fecha_creacion is not None:
            queryset = queryset.filter(fecha_creacion=fecha_creacion)
        if fecha_aprobado is not None:
            queryset = queryset.filter(fecha_aprobado=fecha_aprobado)
        if fecha_entrega_estimada is not None:
            queryset = queryset.filter(fecha_entrega_estimada=fecha_entrega_estimada)
        if fecha_ordenado is not None:
            queryset = queryset.filter(fecha_ordenado=fecha_ordenado)
        if motivo is not None:
            queryset = queryset.filter(motivo__icontains=motivo)
        if total is not None:
            queryset = queryset.filter(total=total)
        if usuario_id is not None:
            queryset = queryset.filter(usuario__id=usuario_id)
        if proveedor_id is not None:
            queryset = queryset.filter(proveedor__id=proveedor_id)
        if tipo_de_cambio is not None:
            queryset = queryset.filter(tipo_de_cambio=tipo_de_cambio)
        if departamento_nombre is not None:
            queryset = queryset.filter(usuario__departamento__nombre=departamento_nombre)
            queryset = queryset.filter(Q(proyecto__isnull=True) | Q(proyecto__nombre=''))
        if aprobado is not None:
            aprobado = aprobado.upper()
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

class RackViewSet(viewsets.ModelViewSet):
    queryset = Rack.objects.all()
    serializer_class = RackSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Rack.objects.all().order_by('-id')
        nombre = self.request.query_params.get('nombre', None)
        productID = self.request.query_params.get('productID', None)

        if nombre is not None:
            queryset = queryset.filter(nombre__icontains=nombre)

        if productID is not None:
            producto = ProductoAlmacen.objects.get(id=productID)
            queryset = queryset.filter(estantes__productos=producto)

        return queryset

    def list(self, request, *args, **kwargs):
        productID = request.query_params.get('productID', None)

        if productID is not None:
            producto = ProductoAlmacen.objects.get(id=productID)
            estante = Estante.objects.get(productos=producto)
            rack = self.get_queryset().get(id=estante.rack.id)
            serializer = self.get_serializer(rack)
            data = serializer.data
            data['estante'] = estante.numero
            return Response(data)

        return super().list(request, *args, **kwargs)

class EstanteViewSet(viewsets.ModelViewSet):
    queryset = Estante.objects.all().order_by('-id')
    serializer_class = EstanteSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Estante.objects.all().order_by('-id')
        
        rack_id = self.request.query_params.get('rack', None)
        estante_numero = self.request.query_params.get('estante', None)

        if rack_id is not None:
            queryset = queryset.filter(rack__id=rack_id)

        if estante_numero is not None:
            queryset = queryset.filter(numero=estante_numero)

        return queryset

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all().order_by('-id')
    serializer_class = PedidoSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        fecha_pedido = self.request.query_params.get('fecha', None)
        usuario_nombre = self.request.query_params.get('usuario', None)
        producto_nombre = self.request.query_params.get('producto', None)
        cantidad = self.request.query_params.get('cantidad', None)

        if fecha_pedido is not None:
            try:
                if '/' in fecha_pedido:
                    fecha_desde, fecha_hasta = fecha_pedido.split('/')
                    parsed_fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d')
                    parsed_fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d')
                    queryset = queryset.filter(
                        fecha_pedido__range=(parsed_fecha_desde, parsed_fecha_hasta)
                    )
                else:
                    parsed_date = datetime.strptime(fecha_pedido, '%Y-%m-%d')
                    queryset = queryset.filter(
                        fecha_pedido__year=parsed_date.year,
                        fecha_pedido__month=parsed_date.month,
                        fecha_pedido__day=parsed_date.day
                    )
            except ValueError:
                queryset = queryset.none()
            
        if usuario_nombre is not None:
            queryset = queryset.filter(usuario_nombre__icontains=usuario_nombre)
            
        if producto_nombre is not None:
            queryset = queryset.filter(producto_nombre__icontains=producto_nombre)
            
        if cantidad is not None:
            if '>' in cantidad and '<' in cantidad:
                min_cantidad, max_cantidad = cantidad.split('<')
                min_cantidad = min_cantidad.replace('>', '')
                queryset = queryset.filter(cantidad__gt=min_cantidad, cantidad__lt=max_cantidad)
            elif '>' in cantidad:
                min_cantidad = cantidad.replace('>', '')
                queryset = queryset.filter(cantidad__gt=min_cantidad)
            elif '<' in cantidad:
                max_cantidad = cantidad.replace('<', '')
                queryset = queryset.filter(cantidad__lt=max_cantidad)
            else:
                queryset = queryset.filter(cantidad=cantidad)

        return queryset

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
        limit = self.request.query_params.get('limit', None)
        hayEntrega = self.request.query_params.get('hayEntrega', None)

        if id is not None:
            queryset = queryset.annotate(id_str=Cast('id', CharField())).filter(id_str__icontains=id)
        
        if hayEntrega is not None:
            hayEntrega = hayEntrega.lower() in ['true', '1']
            if hayEntrega:
                queryset = queryset.exclude(fecha_entrega__isnull=True)
            else:
                queryset = queryset.filter(fecha_entrega__isnull=True)
        
        if fecha_inicio is not None and fecha_fin is not None:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
            queryset = queryset.filter(fecha_entrega__range=[fecha_inicio, fecha_fin])
        elif fecha_inicio is not None:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            queryset = queryset.filter(fecha_entrega__gte=fecha_inicio)
        elif fecha_fin is not None:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
            queryset = queryset.filter(fecha_entrega__lte=fecha_fin)

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
            
        if limit is not None:
            try:
                limit = int(limit)
                queryset = queryset[:limit]
            except ValueError:
                pass
        
        return queryset

    def list(self, request, *args, **kwargs):
        count = request.query_params.get('count', 'false').lower() == 'true'
        if count:
            queryset = self.filter_queryset(self.get_queryset())
            count = queryset.count()
            return Response({'ordenes': count})
        else:
            return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def actualizar_productos_recibidos(self, request, pk=None):
        orden = self.get_object()
        productos_data = request.data

        productos_almacen = []

        for producto_data in productos_data:
            id_producto = producto_data.get('id')
            cantidad_recibida = producto_data.get('cantidad_recibida')

            producto_requisicion = get_object_or_404(orden.requisicion.productos, id=id_producto)

            producto_requisicion.cantidad_recibida += cantidad_recibida
            producto_requisicion.save()

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

            producto_almacen.cantidad += cantidad_recibida
            producto_almacen.save()

            productos_almacen.append(ProductoAlmacenSerializer(producto_almacen).data)

        todos_recibidos = all(producto.cantidad <= producto.cantidad_recibida for producto in orden.requisicion.productos.all())

        if todos_recibidos:
            orden.orden_recibida = True
            orden.estado = "EN ALMACEN"
            orden.save()

        orden = self.get_object()

        serializer = self.get_serializer(orden)
        data = serializer.data
        # Añadir la lista de productos de almacén a la respuesta
        data['productos_almacen'] = productos_almacen
        return Response(data)



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
