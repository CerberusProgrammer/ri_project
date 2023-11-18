from rest_framework import viewsets, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from django.db.models import Count, Min, Max, Sum, F,DurationField, ExpressionWrapper
from rest_framework import status
from django.db.models import Q

from ri_compras.models import Usuarios
from ri_compras.serializer import UsuariosSerializer, UsuariosVerySimpleSerializer

from .models import Material, Notificacion, Placa, Proceso, Pieza
from .serializers import MaterialSerializer, NotificacionSerializer, PlacaSerializer, ProcesoSerializer, PiezaSerializer

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'espesor', 'proveedor']
    ordering_fields = ['nombre', 'espesor']

class PlacaViewSet(viewsets.ModelViewSet):
    queryset = Placa.objects.all().order_by('-id')
    serializer_class = PlacaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['piezas']
    ordering_fields = ['piezas']

class ProcesoViewSet(viewsets.ModelViewSet):
    queryset = Proceso.objects.all().order_by('-id')
    serializer_class = ProcesoSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'estatus', 'maquina']
    ordering_fields = ['nombre', 'estatus', 'maquina']

    @action(detail=False, methods=['get'])
    def porcentaje_realizados_hoy(self, request):
        procesos_hoy = [proceso for proceso in Proceso.objects.all() if proceso.inicioProceso.date() == timezone.now().date()]

        procesos_realizados_hoy = [proceso for proceso in procesos_hoy if proceso.estatus == 'realizado']
        porcentaje_realizados_hoy = len(procesos_realizados_hoy) / len(procesos_hoy) * 100 if procesos_hoy else 0

        return Response({"porcentaje_realizados_hoy": porcentaje_realizados_hoy})

    @action(detail=False, methods=['get'])
    def personal(self, request):
        mis_procesos = Proceso.objects.filter(realizadoPor=request.user)

        if not mis_procesos:
            return Response({"message": "No has realizado ningún proceso."})

        serializer = self.get_serializer(mis_procesos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def usuario_mas_procesos_hoy(self, request):
        hoy = timezone.now().date()

        usuarios = Usuarios.objects.filter(proceso__inicioProceso__date=hoy)
        usuarios = usuarios.annotate(num_procesos=Count('proceso'))

        usuario_mas_procesos = usuarios.order_by('-num_procesos').first()

        if not usuario_mas_procesos:
            return Response({"message": "No hay ningún usuario que haya realizado un proceso hoy."})

        procesos_hoy_ids = usuario_mas_procesos.proceso_set.filter(inicioProceso__date=hoy).values_list('id', flat=True)
        usuario_mas_procesos.procesos_hoy_ids = list(procesos_hoy_ids)

        serializer = UsuariosVerySimpleSerializer(usuario_mas_procesos)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def procesos_rechazados(self, request):
        procesos_rechazados = Proceso.objects.filter(estatus='rechazado')
        serializer = self.get_serializer(procesos_rechazados, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def procesos_operando(self, request):
        procesos_operando = Proceso.objects.filter(estatus='operando')
        serializer = self.get_serializer(procesos_operando, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def procesos_completados(self, request):
        procesos_completados = Proceso.objects.filter(estatus='realizado')
        serializer = self.get_serializer(procesos_completados, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def procesos_pendientes(self, request):
        procesos_pendientes = Proceso.objects.filter(estatus='pendiente')
        serializer = self.get_serializer(procesos_pendientes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def procesos_prioritarios(self, request):
        procesos_prioritarios = Proceso.objects.filter(prioridad=True)
        serializer = self.get_serializer(procesos_prioritarios, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def contar_procesos_pendientes(self, request):
        count = Proceso.objects.filter(estatus='pendiente').count()
        return Response({"count": count})

    @action(detail=False, methods=['get'])
    def contar_procesos_prioritarios(self, request):
        count = Proceso.objects.filter(prioridad=True).count()
        return Response({"count": count})

    @action(detail=False, methods=['get'])
    def contar_procesos_del_dia(self, request):
        hoy = timezone.now().date()
        count = Proceso.objects.filter(inicioProceso__date=hoy).count()
        return Response({"count": count})

class PiezaViewSet(viewsets.ModelViewSet):
    queryset = Pieza.objects.all().order_by('-id')
    serializer_class = PiezaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['consecutivo', 'ordenCompra']
    ordering_fields = ['consecutivo', 'ordenCompra']
    
    @action(detail=False, methods=['get'])
    def ultima_pieza_creada(self, request):
        ultima_pieza = Pieza.objects.latest('fechaCreado')
        serializer = self.get_serializer(ultima_pieza)
        return Response(serializer.data)
    
    def pieza_create(request):
        if request.method == 'POST':
            serializer = PiezaSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def piezas_pendientes(self, request):
        piezas_pendientes = Pieza.objects.filter(estatus='pendiente')
        serializer = self.get_serializer(piezas_pendientes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def piezas_rechazadas(self, request):
        piezas_rechazadas = Pieza.objects.filter(estatus='rechazado')
        serializer = self.get_serializer(piezas_rechazadas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def piezas_aprobadas(self, request):
        piezas_aprobadas = Pieza.objects.filter(estatus='aprobado')
        serializer = self.get_serializer(piezas_aprobadas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def ultimas_piezas_pendientes(self, request):
        ultimas_piezas_pendientes = Pieza.objects.filter(estatus='pendiente').order_by('-fechaCreado')[:5]
        serializer = self.get_serializer(ultimas_piezas_pendientes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def ultimas_piezas_rechazadas(self, request):
        ultimas_piezas_rechazadas = Pieza.objects.filter(estatus='rechazado').order_by('-fechaCreado')[:5]
        serializer = self.get_serializer(ultimas_piezas_rechazadas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def ultimas_piezas_aprobadas(self, request):
        ultimas_piezas_aprobadas = Pieza.objects.filter(estatus='aprobado').order_by('-fechaCreado')[:5]
        serializer = self.get_serializer(ultimas_piezas_aprobadas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def contador_piezas_pendientes(self, request):
        count = Pieza.objects.filter(estatus='pendiente').count()
        return Response({"contador_piezas_pendientes": count})

    @action(detail=False, methods=['get'])
    def contador_piezas_rechazadas(self, request):
        count = Pieza.objects.filter(estatus='rechazado').count()
        return Response({"contador_piezas_rechazadas": count})

    @action(detail=False, methods=['get'])
    def contador_piezas_aprobadas(self, request):
        count = Pieza.objects.filter(estatus='aprobado').count()
        return Response({"contador_piezas_aprobadas": count})

    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        piezas_pendientes = Pieza.objects.filter(procesos__estatus='pendiente')
        serializer = self.get_serializer(piezas_pendientes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def prioritarios(self, request):
        piezas_prioridad = Pieza.objects.filter(prioridad=True)
        serializer = self.get_serializer(piezas_prioridad, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def hoy(self, request):
        piezas_hoy = [pieza for pieza in Pieza.objects.all() if any(proceso.inicioProceso.date() == timezone.now().date() for proceso in pieza.procesos.all())]

        if not piezas_hoy:
            return Response({"detail": "No hay ninguna pieza con un proceso que comienza hoy."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(piezas_hoy, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def porcentaje_realizadas_hoy(self, request):
        piezas_hoy = [pieza for pieza in Pieza.objects.all() if any(proceso.inicioProceso.date() == timezone.now().date() for proceso in pieza.procesos.all())]

        piezas_realizadas_hoy = [pieza for pieza in piezas_hoy if all(proceso.estatus == 'realizado' for proceso in pieza.procesos.all())]

        porcentaje_realizadas_hoy = len(piezas_realizadas_hoy) / len(piezas_hoy) * 100 if piezas_hoy else 0

        return Response({"porcentaje_realizadas_hoy": porcentaje_realizadas_hoy})

    @action(detail=False, methods=['get'])
    def obtener_piezas_sin_asignaciones(self, request):
        piezas_sin_asignaciones = Pieza.objects.filter(
            material__isnull=True,
            placas__isnull=True,
            procesos__isnull=True,
            estatus='aprobado',
            estatusAsignacion=False
        )
        serializer = self.get_serializer(piezas_sin_asignaciones, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def obtener_piezas_sin_procesos(self, request):
        piezas_sin_procesos = Pieza.objects.filter(
            procesos__isnull=True,
            estatus='aprobado',
            estatusAsignacion=False
        )
        serializer = self.get_serializer(piezas_sin_procesos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def obtener_piezas_sin_placa_asignado(self, request):
        piezas_sin_placa_asignado = Pieza.objects.filter(
            placas__isnull=True,
            estatus='aprobado',
            estatusAsignacion=False
        )
        serializer = self.get_serializer(piezas_sin_placa_asignado, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def obtener_piezas_sin_material_asignado(self, request):
        piezas_sin_material_asignado = Pieza.objects.filter(
            material__isnull=True,
            estatus='aprobado',
            estatusAsignacion=False
        )
        serializer = self.get_serializer(piezas_sin_material_asignado, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def obtener_piezas_terminadas_sin_asignacion_confirmada(self, request):
        piezas_terminadas_sin_asignacion_confirmada = Pieza.objects.filter(
            material__isnull=False,
            placas__isnull=False,
            procesos__isnull=False,
            estatus='aprobado',
            estatusAsignacion=False
        )
        serializer = self.get_serializer(piezas_terminadas_sin_asignacion_confirmada, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def contar_piezas_sin_asignacion(self, request):
        count = Pieza.objects.filter(
            estatus='aprobado',
            placas__isnull=True,
            procesos__isnull=True,
            material__isnull=True
        ).count()
        return Response({"count": count})
    
    @action(detail=False, methods=['get'])
    def contar_piezas_pendientes_de_aprobar(self, request):
        count = Pieza.objects.filter(estatus='pendiente').count()
        return Response({"count": count})

class NotificacionViewSet(viewsets.ModelViewSet):
    queryset = Notificacion.objects.all().order_by('-id')
    serializer_class = NotificacionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    
    @action(detail=False, url_path='usuario/(?P<usuario_id>\d+)')
    def notificaciones_por_usuario(self, request, usuario_id=None):
        notificaciones = self.get_queryset().filter(usuario__id=usuario_id)
        serializer = self.get_serializer(notificaciones, many=True)
        return Response(serializer.data)
    
    @action(detail=False, url_path='usuario/(?P<usuario_id>\d+)/count')
    def count_notificaciones_por_usuario(self, request, usuario_id=None):
        count = self.get_queryset().filter(usuario__id=usuario_id, leido=False).count()
        return Response({'count': count})

    @action(detail=False, url_path='usuario/(?P<usuario_id>\d+)/has_notifications')
    def has_notifications(self, request, usuario_id=None):
        has_notifications = self.get_queryset().filter(usuario__id=usuario_id, leido=False).exists()
        return Response({'has_notifications': has_notifications})