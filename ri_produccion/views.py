from django.shortcuts import get_object_or_404
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
    
    @action(detail=True, methods=['put'], url_path='asignar_placa_a_pieza/(?P<placa_id>\d+)')
    def asignar_placa_a_pieza(self, request, pk=None, placa_id=None):
        pieza = self.get_object()
        try:
            placa = Placa.objects.get(id=placa_id)
        except Placa.DoesNotExist:
            return Response({"error": "Placa does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        if placa in pieza.placas.all():
            return Response({"error": "Placa is already associated with this Pieza"}, status=status.HTTP_400_BAD_REQUEST)

        pieza.placas.add(placa)
        pieza.save()

        return Response({"success": f"Placa {placa_id} has been successfully assigned to Pieza {pieza.consecutivo}"}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='buscar_piezas_por_material_espesor')
    def buscar_piezas_por_material_espesor(self, request):
        material_nombre = request.data.get('material')
        espesor = request.data.get('espesor')

        if not all([material_nombre, espesor]):
            return Response({"error": "Los parámetros 'material' y 'espesor' son requeridos"}, status=status.HTTP_400_BAD_REQUEST)

        material = Material.objects.filter(nombre=material_nombre, espesor=espesor).first()
        if material is None:
            return Response([], status=status.HTTP_200_OK)

        piezas = Pieza.objects.filter(material=material, estatusAsignacion=False)

        serializer = PiezaSerializer(piezas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='agregar_procesos_a_pieza')
    def agregar_procesos_a_pieza(self, request, pk=None):
        pieza = self.get_object()
        procesos_data = request.data.get('procesos')
        if not procesos_data:
            return Response({"error": "The 'procesos' parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Eliminar los Proceso existentes
        pieza.procesos.all().delete()

        for proceso_data in procesos_data:
            placa_id = proceso_data.get('placa_id')
            if not placa_id:
                return Response({"error": "The 'placa_id' parameter is required for each proceso"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                placa = Placa.objects.get(id=placa_id)
            except Placa.DoesNotExist:
                return Response({"error": f"Placa with id {placa_id} does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            proceso_data['placa'] = placa.id

            # Comprobar si hay conflictos de horario
            inicioProceso = proceso_data.get('inicioProceso')
            finProceso = proceso_data.get('finProceso')
            maquina = proceso_data.get('maquina')
            conflictos = Proceso.objects.filter(maquina=maquina, inicioProceso__lt=finProceso, finProceso__gt=inicioProceso)
            if conflictos.exists():
                conflicto = conflictos.first()
                return Response({"error": f"Horario de proceso en conflicto con el proceso '{conflicto.nombre}' que tiene horario de {conflicto.inicioProceso} a {conflicto.finProceso}"}, status=status.HTTP_400_BAD_REQUEST)

            proceso_serializer = ProcesoSerializer(data=proceso_data)
            if proceso_serializer.is_valid():
                proceso = proceso_serializer.save()
                pieza.procesos.add(proceso)
            else:
                return Response(proceso_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        pieza.save()

        # Serializar y devolver el objeto Pieza
        pieza_serializer = PiezaSerializer(pieza)
        return Response(pieza_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], url_path='agregar_placa_a_pieza/(?P<placa_id>\d+)')
    def agregar_placa_a_pieza(self, request, pk=None, placa_id=None):
        pieza = self.get_object()
        try:
            placa = Placa.objects.get(id=placa_id)
        except Placa.DoesNotExist:
            return Response({"error": "Placa does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        if placa in pieza.placas.all():
            return Response({"error": "Placa is already associated with this Pieza"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the number of pieces to assign from the request data
        piezas_asignar = request.data.get('piezas_asignar')
        if not piezas_asignar:
            return Response({"error": "The 'piezas_asignar' parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate the total pieces from all the plates associated with the piece
        total_piezas = sum(p.piezas for p in pieza.placas.all())
        # Add the pieces to assign from the new plate
        total_piezas += piezas_asignar

        if total_piezas > pieza.piezasTotales:
            return Response({
                "error": "Adding this Placa exceeds the total number of pieces allowed",
                "allowed_pieces": pieza.piezasTotales - total_piezas + piezas_asignar
            }, status=status.HTTP_400_BAD_REQUEST)
        elif total_piezas <= pieza.piezasTotales:
            # Update the number of pieces in the plate
            placa.piezas = piezas_asignar
            placa.save()

            pieza.placas.add(placa)
            serializer = PlacaSerializer(placa)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], url_path='cambiar_placa_a_pieza/(?P<placa_id>\d+)')
    def cambiar_placa_a_pieza(self, request, pk=None, placa_id=None):
        pieza = self.get_object()
        try:
            placa = Placa.objects.get(id=placa_id)
        except Placa.DoesNotExist:
            return Response({"error": "Placa does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        if placa not in pieza.placas.all():
            return Response({"error": "Placa is not associated with this Pieza"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = PlacaSerializer(placa, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'], url_path='quitar_placa_a_pieza/(?P<placa_id>\d+)')
    def quitar_placa_a_pieza(self, request, pk=None, placa_id=None):
        pieza = self.get_object()
        try:
            placa = Placa.objects.get(id=placa_id)
        except Placa.DoesNotExist:
            return Response({"error": "Placa does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        if placa not in pieza.placas.all():
            return Response({"error": "Placa is not associated with this Pieza"}, status=status.HTTP_400_BAD_REQUEST)
        pieza.placas.remove(placa)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def progreso_de_piezas_con_asignacion(self, request):
        total_piezas = Pieza.objects.filter(estatus='pendiente').count()
        piezas_aprobadas = Pieza.objects.filter(estatus='aprobado', estatusAsignacion=True).count()
        if total_piezas == 0:
            return Response({"error": "No pending Piezas"}, status=status.HTTP_400_BAD_REQUEST)
        progreso = (piezas_aprobadas / total_piezas) * 100
        return Response({"progreso": progreso}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['put'])
    def rechazar_pieza(self, request, pk=None):
        pieza = self.get_object()
        pieza.estatus = 'rechazado'
        pieza.save()
        return Response({"message": "Pieza rejected successfully"}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['put'])
    def aprobar_pieza(self, request, pk=None):
        pieza = self.get_object()
        pieza.estatus = 'aprobado'
        pieza.save()
        return Response({"message": "Pieza approved successfully"}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['put'])
    def terminar_asignacion_pieza(self, request, pk=None):
        pieza = self.get_object()
        pieza.estatusAsignacion = True
        pieza.save()
        return Response({"message": "Pieza assignment status updated successfully"}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def agregar_material_a_pieza(self, request, pk=None):
        pieza = self.get_object()
        serializer = MaterialSerializer(data=request.data)
        if serializer.is_valid():
            material = serializer.save()
            pieza.material = material
            pieza.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'], url_path='cambiar_material_a_pieza/(?P<material_id>\d+)')
    def cambiar_material_a_pieza(self, request, pk=None, material_id=None):
        pieza = self.get_object()
        try:
            material = Material.objects.get(id=material_id)
        except Material.DoesNotExist:
            return Response({"error": "Material does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        pieza.material = material
        pieza.save()
        serializer = MaterialSerializer(material)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['delete'], url_path='quitar_material_a_pieza/(?P<material_id>\d+)')
    def quitar_material_a_pieza(self, request, pk=None, material_id=None):
        pieza = self.get_object()
        try:
            material = Material.objects.get(id=material_id)
        except Material.DoesNotExist:
            return Response({"error": "Material does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        if pieza.material != material:
            return Response({"error": "Material is not associated with this Pieza"}, status=status.HTTP_400_BAD_REQUEST)
        pieza.material = None
        pieza.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def agregar_proceso_a_pieza(self, request, pk=None):
        pieza = self.get_object()
        placa_id = request.data.get('placa')  # Get placa_id from request data
        if not placa_id:
            return Response({"error": "placa field is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            placa = Placa.objects.get(id=placa_id)  # Get Placa object
        except Placa.DoesNotExist:
            return Response({"error": "Placa does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ProcesoSerializer(data=request.data)
        if serializer.is_valid():
            proceso = serializer.save(placa=placa)  # Provide placa when saving Proceso
            pieza.procesos.add(proceso)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'], url_path='cambiar_proceso_a_pieza/(?P<proceso_id>\d+)')
    def cambiar_proceso_a_pieza(self, request, pk=None, proceso_id=None):
        pieza = self.get_object()
        try:
            proceso = Proceso.objects.get(id=proceso_id)
        except Proceso.DoesNotExist:
            return Response({"error": "Proceso does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        if proceso not in pieza.procesos.all():
            return Response({"error": "Proceso is not associated with this Pieza"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ProcesoSerializer(proceso, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'], url_path='quitar_proceso_a_pieza/(?P<proceso_id>\d+)')
    def quitar_proceso_a_pieza(self, request, pk=None, proceso_id=None):
        pieza = self.get_object()
        try:
            proceso = Proceso.objects.get(id=proceso_id)
        except Proceso.DoesNotExist:
            return Response({"error": "Proceso does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        if proceso not in pieza.procesos.all():
            return Response({"error": "Proceso is not associated with this Pieza"}, status=status.HTTP_400_BAD_REQUEST)
        pieza.procesos.remove(proceso)  # Remove the Proceso from the Pieza
        proceso.delete()  # Delete the Proceso
        return Response(status=status.HTTP_204_NO_CONTENT)
    
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
            Q(estatus='aprobado'),
            Q(material__isnull=True) | Q(placas__isnull=True) | Q(procesos__isnull=True)
        ).order_by('-fechaCreado').distinct()
        serializer = self.get_serializer(piezas_sin_asignaciones, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def obtener_piezas_sin_procesos(self, request):
        piezas_sin_procesos = Pieza.objects.filter(
            material__isnull=False,
            placas__isnull=False,
            procesos__isnull=True,
            estatus='aprobado',
            estatusAsignacion=False
        )
        serializer = self.get_serializer(piezas_sin_procesos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def obtener_piezas_sin_placa_asignado(self, request):
        piezas_sin_placa_asignado = Pieza.objects.filter(
            material__isnull=False,
            placas__isnull=True,
            procesos__isnull=True,
            estatus='aprobado',
            estatusAsignacion=False
        )
        serializer = self.get_serializer(piezas_sin_placa_asignado, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def obtener_piezas_sin_material_asignado(self, request):
        piezas_sin_material_asignado = Pieza.objects.filter(
            material__isnull=True,
            placas__isnull=True,
            procesos__isnull=True,
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
            Q(estatus='aprobado'),
            Q(material__isnull=True) | Q(placas__isnull=True) | Q(procesos__isnull=True)
        ).order_by('-fechaCreado').distinct().count()
        return Response({"count": count})
    
    @action(detail=False, methods=['get'])
    def contar_piezas_pendientes_de_aprobar(self, request):
        count = Pieza.objects.filter(estatus='pendiente').count()
        return Response({"count": count})
    
    @action(detail=False, methods=['get'])
    def ultimas_piezas_pendientes_de_asignar(self, request):
        piezas_pendientes_de_asignar = Pieza.objects.filter(
            Q(estatus='aprobado'),
            Q(material__isnull=True) | Q(placas__isnull=True) | Q(procesos__isnull=True)
        ).order_by('-fechaCreado').distinct()[:5]
        serializer = PiezaSerializer(piezas_pendientes_de_asignar, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def ultimas_piezas_pendientes_de_aprobar(self, request):
        piezas_pendientes_de_aprobar = Pieza.objects.filter(estatus='pendiente').order_by('-fechaCreado').distinct()[:5]
        serializer = PiezaSerializer(piezas_pendientes_de_aprobar, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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