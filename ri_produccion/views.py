from django.http import JsonResponse
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
from rest_framework.exceptions import NotFound

from django.utils.dateparse import parse_datetime

from django.db.models import Exists, OuterRef
from django.db.models import Q

from ri_compras.models import Usuarios
from ri_compras.serializer import UsuarioDepartamentoSerializer, UsuariosSerializer, UsuariosVerySimpleSerializer

from .models import Material, Notificacion, PiezaPlaca, Placa, Proceso, Pieza
from .serializers import MaterialSerializer, NotificacionSerializer, PlacaSerializer, ProcesoSerializer, PiezaSerializer

from django.db.models import F, ExpressionWrapper, fields
from django.db.models.functions import Coalesce

from ri_produccion import models

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'espesor', 'proveedor']
    ordering_fields = ['nombre', 'espesor']
    
    @action(detail=False, methods=['get'])
    def piezas_para_nesteo_filtrado(self, request):
        # Inicializa una lista vacía para almacenar las piezas que cumplen con las condiciones
        piezas_validas = []

        # Obtiene todas las piezas
        todas_las_piezas = Pieza.objects.all()

        # Itera sobre todas las piezas
        for pieza in todas_las_piezas:
            # Verifica si la pieza requiere nesteo y tiene un valor en el campo material
            if pieza.requiere_nesteo and pieza.material is not None:
                # Calcula el total de piezas realizadas
                piezas_realizadas = pieza.placas.aggregate(total=Sum('piezaplaca__piezas_realizadas'))['total']

                # Si el total de piezas realizadas es menor que el total de piezas, o si la lista de placas está vacía, añade la pieza a la lista de piezas válidas
                if piezas_realizadas is None or piezas_realizadas < pieza.piezasTotales:
                    piezas_validas.append(pieza)

        # Serializa los objetos Pieza
        piezas_serializer = PiezaSerializer(piezas_validas, many=True)

        return Response(piezas_serializer.data)
    
    @action(detail=False, methods=['get'])
    def materiales_para_nesteo_filtrado(self, request):
        # Inicializa una lista vacía para almacenar los nombres de los materiales que cumplen con las condiciones
        nombres_materiales_validos = []

        # Obtiene todas las piezas
        todas_las_piezas = Pieza.objects.all()

        # Itera sobre todas las piezas
        for pieza in todas_las_piezas:
            # Verifica si la pieza requiere nesteo y tiene un valor en el campo material
            if pieza.requiere_nesteo and pieza.material is not None:
                # Calcula el total de piezas realizadas
                piezas_realizadas = pieza.placas.aggregate(total=Sum('piezaplaca__piezas_realizadas'))['total']

                # Si el total de piezas realizadas es menor que el total de piezas, o si la lista de placas está vacía, añade el nombre del material a la lista de nombres de materiales válidos
                if piezas_realizadas is None or piezas_realizadas < pieza.piezasTotales:
                    nombres_materiales_validos.append(pieza.material.nombre)

        # Elimina los duplicados de la lista de nombres de materiales válidos
        nombres_materiales_validos = list(set(nombres_materiales_validos))

        return Response(nombres_materiales_validos)

    @action(detail=False, methods=['post'])
    def espesores_para_nesteo_filtrado(self, request):
        material_name = request.data.get('material')
        if not material_name:
            return Response({"error": "No material name provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Inicializa una lista vacía para almacenar los espesores de los materiales que cumplen con las condiciones
        espesores_materiales_validos = []

        # Obtiene todas las piezas
        todas_las_piezas = Pieza.objects.all()

        # Itera sobre todas las piezas
        for pieza in todas_las_piezas:
            # Verifica si la pieza requiere nesteo, tiene un valor en el campo material y el nombre del material coincide con el nombre proporcionado
            if pieza.requiere_nesteo and pieza.material is not None and pieza.material.nombre == material_name:
                # Calcula el total de piezas realizadas
                piezas_realizadas = pieza.placas.aggregate(total=Sum('piezaplaca__piezas_realizadas'))['total']

                # Si el total de piezas realizadas es menor que el total de piezas, o si la lista de placas está vacía, añade el espesor del material a la lista de espesores de materiales válidos
                if piezas_realizadas is None or piezas_realizadas < pieza.piezasTotales:
                    espesores_materiales_validos.append(pieza.material.espesor)

        # Elimina los duplicados de la lista de espesores de materiales válidos
        espesores_materiales_validos = list(set(espesores_materiales_validos))

        return Response(espesores_materiales_validos)

class PlacaViewSet(viewsets.ModelViewSet):
    queryset = Placa.objects.all().order_by('-id')
    serializer_class = PlacaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['piezas']
    ordering_fields = ['piezas']
    
    @action(detail=False, methods=['get'])
    def obtener_placas_disponibles(self, request):
        # Obtener todas las Placas
        todas_las_placas = Placa.objects.all()

        data = []
        for placa in todas_las_placas:
            # Obtener todas las Piezas asociadas a la Placa actual
            piezas_de_placa = Pieza.objects.filter(placas=placa)

            # Si la Placa no tiene Piezas asociadas o todas las Piezas asociadas tienen estatusAsignacion=False, entonces la Placa está disponible
            if not piezas_de_placa or not any(pieza.estatusAsignacion == True for pieza in piezas_de_placa):
                placa_data = {
                    "id": placa.id,
                    "nombre": placa.nombre,
                    "descripcion": placa.descripcion,
                    "piezas": placa.piezas,
                }
                data.append(placa_data)

        return Response(data)
    
    @action(detail=False, methods=['get'])
    def placas_con_piezas(self, request):
        # Get all Placa objects
        todas_las_placas = Placa.objects.all()
        
        data = []
        for placa in todas_las_placas:
            # Get all Pieza objects associated with the current Placa
            piezas_de_placa = Pieza.objects.filter(
                placas=placa,
                estatus="aprobado",
            )
            
            # If the Placa has no Piezas associated or at least one associated Pieza has estatusAsignacion=False, then the Placa is available
            if not piezas_de_placa or any(pieza.estatusAsignacion == False for pieza in piezas_de_placa):
                # Serializa las piezas
                piezas_data = PiezaSerializer([pieza for pieza in piezas_de_placa if pieza.estatusAsignacion == False], many=True).data
                
                placa_data = {
                    "id": placa.id,
                    "nombre": placa.nombre,
                    "descripcion": placa.descripcion,
                    "piezas": placa.piezas,
                    "piezas_activas": piezas_data
                }
                data.append(placa_data)
        
        data.reverse()
        
        return Response(data)

    @action(detail=True, methods=['get'])
    def obtener_piezas_asignadas_a_placa(self, request, pk=None):
        placa = self.get_object()

        piezas = Pieza.objects.filter(
            placas=placa,
            estatus="aprobado",
        )

        serializer = PiezaSerializer(piezas, many=True)

        return Response(serializer.data)

class ProcesoViewSet(viewsets.ModelViewSet):
    queryset = Proceso.objects.all().order_by('-id')
    serializer_class = ProcesoSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'estatus', 'maquina']
    ordering_fields = ['nombre', 'estatus', 'maquina']

    @action(detail=False, methods=['get'], url_path='mi_progreso_procesos/(?P<id>\d+)')
    def mi_progreso_procesos(self, request, id=None):
        usuario = get_object_or_404(Usuarios, id=id)
        total_procesos = Proceso.objects.filter(realizadoPor=usuario).count()
        procesos_realizados = Proceso.objects.filter(
            Q(realizadoPor=usuario),
            Q(estatus='realizado')
        ).count()

        if total_procesos == 0:
            progreso = 0
        else:
            progreso = procesos_realizados / total_procesos

        return Response({"progreso": progreso})

    @action(detail=False, methods=['get'], url_path='mis_procesos_actuales_cantidad/(?P<id>\d+)')
    def mis_procesos_actuales_cantidad(self, request, id=None):
        current_time = timezone.now()
        usuario = get_object_or_404(Usuarios, id=id)
        cantidad = Proceso.objects.filter(
            Q(realizadoPor=usuario),
            Q(estatus__in=['pendiente', 'operando']),
            Q(inicioProceso__gte=current_time)
        ).count()

        return Response({"cantidad": cantidad})

    @action(detail=False, methods=['get'], url_path='mis_procesos_retrasados_cantidad/(?P<id>\d+)')
    def mis_procesos_retrasados_cantidad(self, request, id=None):
        current_time = timezone.now()
        usuario = get_object_or_404(Usuarios, id=id)
        print(Proceso.objects.filter(
            Q(realizadoPor=usuario),
            Q(estatus__in=['pendiente', 'operando']),
            Q(finProceso__lt=current_time)
        ))
        print('uwu')
        cantidad = Proceso.objects.filter(
            Q(realizadoPor=usuario),
            Q(estatus__in=['pendiente', 'operando']),
            Q(finProceso__lt=current_time)
        ).count()

        return Response({"cantidad": cantidad})

    @action(detail=False, methods=['get'], url_path='mis_procesos_prioritarios_cantidad/(?P<id>\d+)')
    def mis_procesos_prioritarios_cantidad(self, request, id=None):
        usuario = get_object_or_404(Usuarios, id=id)
        piezas_prioritarias = Pieza.objects.filter(prioridad=True)
        cantidad = Proceso.objects.filter(
            Q(realizadoPor=usuario),
            Q(pieza__in=piezas_prioritarias)
        ).distinct().count()

        return Response({"cantidad": cantidad})

    @action(detail=False, methods=['get'], url_path='mis_procesos_actuales/(?P<id>\d+)')
    def mis_procesos_actuales(self, request, id=None):
        current_time = timezone.now()
        usuario = get_object_or_404(Usuarios, id=id)
        procesos = Proceso.objects.filter(
            Q(realizadoPor=usuario),
            Q(estatus__in=['pendiente', 'operando']),
            Q(inicioProceso__gte=current_time)
        ).order_by('inicioProceso')

        response = []
        for proceso in procesos:
            piezas = proceso.pieza_set.all()
            for pieza in piezas:
                response.append({
                    'id': proceso.id,
                    'nombre': proceso.nombre,
                    'estatus': proceso.estatus,
                    'maquina': proceso.maquina,
                    'inicioProceso': proceso.inicioProceso,
                    'finProceso': proceso.finProceso,
                    'terminadoProceso': proceso.terminadoProceso,
                    'comentarios': proceso.comentarios,
                    'prioridad': proceso.prioridad,
                    'piezasRealizadas': proceso.piezasRealizadas,
                    'realizadoPor': proceso.realizadoPor.id if proceso.realizadoPor else None,
                    'pieza_id': pieza.id,
                    'consecutivo': pieza.consecutivo
                })

        return Response(response)

    @action(detail=False, methods=['get'], url_path='mis_procesos_retrasados/(?P<id>\d+)')
    def mis_procesos_retrasados(self, request, id=None):
        current_time = timezone.now()
        usuario = get_object_or_404(Usuarios, id=id)
        procesos = Proceso.objects.filter(
            Q(realizadoPor=usuario),
            Q(estatus__in=['pendiente', 'operando']),
            Q(finProceso__lt=current_time)
        )
        response = []
        for proceso in procesos:
            piezas = proceso.pieza_set.all()
            for pieza in piezas:
                response.append({
                    'id': proceso.id,
                    'nombre': proceso.nombre,
                    'estatus': proceso.estatus,
                    'maquina': proceso.maquina,
                    'inicioProceso': proceso.inicioProceso,
                    'finProceso': proceso.finProceso,
                    'terminadoProceso': proceso.terminadoProceso,
                    'comentarios': proceso.comentarios,
                    'prioridad': proceso.prioridad,
                    'piezasRealizadas': proceso.piezasRealizadas,
                    'realizadoPor': proceso.realizadoPor.id if proceso.realizadoPor else None,
                    'pieza_id': pieza.id,
                    'consecutivo': pieza.consecutivo
                })

        return Response(response)

    @action(detail=False, methods=['get'], url_path='mis_procesos_prioritarios/(?P<id>\d+)')
    def mis_procesos_prioritarios(self, request, id=None):
        usuario = get_object_or_404(Usuarios, id=id)
        piezas_prioritarias = Pieza.objects.filter(prioridad=True)
        procesos = Proceso.objects.filter(
            Q(realizadoPor=usuario),
            Q(pieza__in=piezas_prioritarias)
        ).distinct().order_by('inicioProceso')

        response = []
        for proceso in procesos:
            piezas = proceso.pieza_set.all()
            for pieza in piezas:
                response.append({
                    'id': proceso.id,
                    'nombre': proceso.nombre,
                    'estatus': proceso.estatus,
                    'maquina': proceso.maquina,
                    'inicioProceso': proceso.inicioProceso,
                    'finProceso': proceso.finProceso,
                    'terminadoProceso': proceso.terminadoProceso,
                    'comentarios': proceso.comentarios,
                    'prioridad': proceso.prioridad,
                    'piezasRealizadas': proceso.piezasRealizadas,
                    'realizadoPor': proceso.realizadoPor.id if proceso.realizadoPor else None,
                    'pieza_id': pieza.id,
                    'consecutivo': pieza.consecutivo
                })

        return Response(response)

    @action(detail=False, methods=['get'], url_path='procesos_maquinado_retrasados_piezas')
    def procesos_maquinado_retrasados_piezas(self, request):
        current_time = timezone.now()
        maquinas = ['cnc 1', 'cnc 2', 'fresadora 1', 'fresadora 2', 'torno', 'machueleado', 'limpieza']
        procesos = Proceso.objects.filter(
            Q(realizadoPor__isnull=False),
            Q(estatus__in=['pendiente', 'operando']),
            Q(maquina__iexact=maquinas),
            Q(finProceso__lt=current_time)
        ).order_by('inicioProceso')

        serializer = ProcesoSerializer(procesos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='procesos_soldadura_retrasados_piezas')
    def procesos_soldadura_retrasados_piezas(self, request):
        current_time = timezone.now()
        maquinas = ['corte', 'pintura', 'pulido']
        procesos = Proceso.objects.filter(
            Q(realizadoPor__isnull=False),
            Q(estatus__in=['pendiente', 'operando']),
            Q(maquina__iexact=maquinas),
            Q(finProceso__lt=current_time)
        ).order_by('inicioProceso')

        serializer = ProcesoSerializer(procesos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='procesos_sm_retrasados_piezas')
    def procesos_sm_retrasados_piezas(self, request):
        current_time = timezone.now()
        maquinas = ['cortadora laser', 'dobladora', 'machueleado', 'limpieza']
        procesos = Proceso.objects.filter(
            Q(realizadoPor__isnull=False),
            Q(estatus__in=['pendiente', 'operando']),
            Q(maquina__iexact=maquinas),
            Q(finProceso__lt=current_time)
        ).order_by('inicioProceso')

        serializer = ProcesoSerializer(procesos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='procesos_maquinado_por_asignar')
    def procesos_maquinado_por_asignar(self, request):
        maquinas = ['cnc 1', 'cnc 2', 'fresadora 1', 'fresadora 2', 'torno', 'machueleado', 'limpieza']
        procesos = Proceso.objects.filter(
            Q(realizadoPor__isnull=True),
            Q(estatus='pendiente'),
            Q(maquina__in=maquinas)
        )

        serializer = ProcesoSerializer(procesos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='procesos_soldadura_por_asignar')
    def procesos_soldadura_por_asignar(self, request):
        maquinas = ['corte', 'pintura', 'pulido']
        procesos = Proceso.objects.filter(
            Q(realizadoPor__isnull=True),
            Q(estatus='pendiente'),
            Q(maquina__in=maquinas)
        )

        serializer = ProcesoSerializer(procesos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='procesos_sm_por_asignar')
    def procesos_sm_por_asignar(self, request):
        maquinas = ['cortadora laser', 'dobladora', 'machueleado', 'limpieza']
        procesos = Proceso.objects.filter(
            Q(realizadoPor__isnull=True),
            Q(estatus='pendiente'),
            Q(maquina__in=maquinas)
        )

        serializer = ProcesoSerializer(procesos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='procesos_maquinado_actuales_piezas')
    def procesos_maquinado_actuales_piezas(self, request):
        maquinas = ['cnc 1', 'cnc 2', 'fresadora 1', 'fresadora 2', 'torno', 'machueleado', 'limpieza']
        procesos = Proceso.objects.filter(
            Q(realizadoPor__isnull=False),
            Q(estatus__in=['pendiente', 'operando']),
            Q(maquina__iexact=maquinas)
        ).order_by('inicioProceso')

        serializer = ProcesoSerializer(procesos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='procesos_soldadura_actuales_piezas')
    def procesos_soldadura_actuales_piezas(self, request):
        maquinas = ['corte', 'pintura', 'pulido']
        procesos = Proceso.objects.filter(
            Q(realizadoPor__isnull=False),
            Q(estatus__in=['pendiente', 'operando']),
            Q(maquina__iexact=maquinas)
        ).order_by('inicioProceso')

        serializer = ProcesoSerializer(procesos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='procesos_sm_actuales_piezas')
    def procesos_sm_actuales_piezas(self, request):
        maquinas = ['cortadora laser', 'dobladora', 'machueleado', 'limpieza']
        procesos = Proceso.objects.filter(
            Q(realizadoPor__isnull=False),
            Q(estatus__in=['pendiente', 'operando']),
            Q(maquina__iexact=maquinas)
        ).order_by('inicioProceso')

        serializer = ProcesoSerializer(procesos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='obtener_estadisticas_tiempos_maquinado_hoy')
    def obtener_estadisticas_tiempos_maquinado_hoy(self, request):
        current_date = timezone.now().date()
        maquinas = ['cnc 1', 'cnc 2', 'fresadora 1', 'fresadora 2', 'torno', 'machueleado', 'limpieza']
        estadisticas = {}

        for maquina in maquinas:
            procesos = Proceso.objects.filter(
                maquina=maquina,
                estatus='realizado',
                inicioProceso__date=current_date,
            )

            tiempo_excedente = ExpressionWrapper(
                Coalesce(F('terminadoProceso'), timezone.now()) - F('finProceso'),
                output_field=fields.DurationField()
            )
            procesos = procesos.annotate(tiempo_excedente=tiempo_excedente)

            total_excedente = sum(
                proceso.tiempo_excedente.total_seconds() / 60
                for proceso in procesos
                if proceso.tiempo_excedente.total_seconds() > 0
            )

            estadisticas[maquina] = int(total_excedente)

        return Response(estadisticas)
    
    @action(detail=False, methods=['get'], url_path='obtener_estadisticas_tiempos_soldadura_hoy')
    def obtener_estadisticas_tiempos_soldadura_hoy(self, request):
        current_date = timezone.now().date()
        maquinas = ['corte', 'pintura', 'pulido']
        estadisticas = {}

        for maquina in maquinas:
            procesos = Proceso.objects.filter(
                maquina=maquina,
                estatus='realizado',
                inicioProceso__date=current_date,
            )

            tiempo_excedente = ExpressionWrapper(
                Coalesce(F('terminadoProceso'), timezone.now()) - F('finProceso'),
                output_field=fields.DurationField()
            )
            procesos = procesos.annotate(tiempo_excedente=tiempo_excedente)

            total_excedente = sum(
                proceso.tiempo_excedente.total_seconds() / 60
                for proceso in procesos
                if proceso.tiempo_excedente.total_seconds() > 0
            )

            estadisticas[maquina] = int(total_excedente)

        return Response(estadisticas)
    
    @action(detail=False, methods=['get'], url_path='obtener_estadisticas_tiempos_sm_hoy')
    def obtener_estadisticas_tiempos_sm_hoy(self, request):
        current_date = timezone.now().date()
        maquinas = ['cortadora laser', 'dobladora', 'machueleado', 'limpieza']
        estadisticas = {}

        for maquina in maquinas:
            procesos = Proceso.objects.filter(
                maquina=maquina,
                estatus='realizado',
                inicioProceso__date=current_date,
            )

            tiempo_excedente = ExpressionWrapper(
                Coalesce(F('terminadoProceso'), timezone.now()) - F('finProceso'),
                output_field=fields.DurationField()
            )
            procesos = procesos.annotate(tiempo_excedente=tiempo_excedente)

            total_excedente = sum(
                proceso.tiempo_excedente.total_seconds() / 60
                for proceso in procesos
                if proceso.tiempo_excedente.total_seconds() > 0
            )

            estadisticas[maquina] = int(total_excedente)

        return Response(estadisticas)
    
    @action(detail=False, methods=['get'])
    def obtener_usuarios_con_procesos_pendientes(self, request):
        now = timezone.now()
        procesos_pendientes = Proceso.objects.filter(finProceso__lt=now, placa__estatusAsignacion=True, estatus='pendiente')
        serializer = ProcesoSerializer(procesos_pendientes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def obtener_todos_los_usuarios_operadores(self, request):
        operadores = Usuarios.objects.filter(rol='OPERADOR', departamento__nombre='Produccion')
        serializer = UsuarioDepartamentoSerializer(operadores, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def obtener_usuarios_trabajando_en_procesos(self, request):
        now = timezone.now()
        procesos_activos = Proceso.objects.filter(inicioProceso__lte=now, finProceso__gte=now, estatus='operando')
        serializer = ProcesoSerializer(procesos_activos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def obtener_usuarios_con_procesos_pendientes(self, request):
        now = timezone.now()
        procesos_pendientes = Proceso.objects.filter(finProceso__gt=now, estatus__in=['pendiente', 'operando'])
        serializer = ProcesoSerializer(procesos_pendientes, many=True)
        return Response(serializer.data)

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
    
    @action(detail=False, methods=['get'], url_path='obtener_procesos_usuario/(?P<id>\d+)')
    def obtener_procesos_usuario(self, request, id=None):
        usuario = get_object_or_404(Usuarios, id=id)
        procesos = Proceso.objects.filter(realizadoPor=usuario)

        serializer = ProcesoSerializer(procesos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def usuario_mas_procesos_hoy(self, request):
        hoy = timezone.now().date()

        usuarios = Usuarios.objects.filter(proceso__inicioProceso__date=hoy)
        usuarios = usuarios.annotate(num_procesos=Count('proceso'))

        usuario_mas_procesos = usuarios.order_by('-num_procesos').first()

        if not usuario_mas_procesos:
            content = {"message": "No hay ningún usuario que haya realizado un proceso hoy."}
            return JsonResponse(content, status=404)

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
    
    @action(detail=False, methods=['get'], url_path='progreso_tasa_error_piezas')
    def progreso_tasa_error_piezas(self, request):
        piezas_revision = Pieza.objects.filter(estatus='revision')

        if not piezas_revision.exists():
            return Response({"tasa_error": 0})

        total_piezas = piezas_revision.aggregate(total=Sum('piezasTotales'))['total']
        total_piezas_rechazadas = piezas_revision.aggregate(total=Sum('piezasRechazadas'))['total']

        if total_piezas == 0:
            return Response({"tasa_error": 0})

        tasa_error = total_piezas_rechazadas / total_piezas

        return Response({"tasa_error": tasa_error})
    
    @action(detail=False, methods=['get'], url_path='progreso_inspeccion_dimensional')
    def progreso_inspeccion_dimensional(self, request):
        total_piezas = Pieza.objects.filter(
            estatus='revision',
            tipo_calidad='dimensional',
            piezaRealizada=True
        ).count()

        piezas_realizadas = Pieza.objects.filter(
            estatus='revision',
            tipo_calidad='dimensional',
            piezaRealizada=True
        ).count()

        if total_piezas == 0:
            return Response({"progreso": 0})

        progreso = piezas_realizadas / total_piezas

        return Response({"progreso": progreso})
    
    @action(detail=False, methods=['get'], url_path='progreso_inspeccion_pintura')
    def progreso_inspeccion_pintura(self, request):
        total_piezas = Pieza.objects.filter(
            estatus='revision',
            tipo_calidad='pintura',
            piezaRealizada=True
        ).count()

        piezas_realizadas = Pieza.objects.filter(
            estatus='revision',
            tipo_calidad='pintura',
            piezaRealizada=True
        ).count()

        if total_piezas == 0:
            return Response({"progreso": 0})

        progreso = piezas_realizadas / total_piezas

        return Response({"progreso": progreso})
    
    @action(detail=False, methods=['get'], url_path='progreso_inspeccion_proveedor')
    def progreso_inspeccion_proveedor(self, request):
        total_piezas = Pieza.objects.filter(
            estatus='revision',
            tipo_calidad='proveedor',
            piezaRealizada=True
        ).count()

        piezas_realizadas = Pieza.objects.filter(
            estatus='revision',
            tipo_calidad='proveedor',
            piezaRealizada=True
        ).count()

        if total_piezas == 0:
            return Response({"progreso": 0})

        progreso = piezas_realizadas / total_piezas

        return Response({"progreso": progreso})
    
    @action(detail=False, methods=['get'], url_path='ultimas_piezas_pendientes_revision_dimensional')
    def ultimas_piezas_pendientes_revision_dimensional(self, request):
        piezas_pendientes = Pieza.objects.filter(
            estatus='revision',
            tipo_calidad='dimensional',
            piezaRealizada=False
        ).order_by('-id')[:5]
        
        if not piezas_pendientes:
            raise NotFound("No hay piezas pendientes de revisión dimensional.")

        serializer = self.get_serializer(piezas_pendientes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='ultimas_piezas_pendientes_revision_pintura')
    def ultimas_piezas_pendientes_revision_pintura(self, request):
        piezas_pendientes = Pieza.objects.filter(
            estatus='revision',
            tipo_calidad='pintura',
            piezaRealizada=False
        ).order_by('-id')[:5]

        serializer = self.get_serializer(piezas_pendientes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='ultimas_piezas_pendientes_revision_proveedor')
    def ultimas_piezas_pendientes_revision_proveedor(self, request):
        piezas_pendientes = Pieza.objects.filter(
            estatus='revision',
            tipo_calidad='proveedor',
            piezaRealizada=False
        ).order_by('-id')[:5]
        
        if not piezas_pendientes:
            raise NotFound("No hay piezas pendientes de revisión proveedor.")

        serializer = self.get_serializer(piezas_pendientes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='piezas_pendientes_revision_dimensional')
    def piezas_pendientes_revision_dimensional(self, request):
        piezas_pendientes = Pieza.objects.filter(
            estatus='revision',
            tipo_calidad='dimensional',
            piezaRealizada=False
        )

        serializer = self.get_serializer(piezas_pendientes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='piezas_pendientes_revision_pintura')
    def piezas_pendientes_revision_pintura(self, request):
        piezas_pendientes = Pieza.objects.filter(
            estatus='revision',
            tipo_calidad='pintura',
            piezaRealizada=False
        )

        serializer = self.get_serializer(piezas_pendientes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='piezas_pendientes_revision_proveedor')
    def piezas_pendientes_revision_proveedor(self, request):
        piezas_pendientes = Pieza.objects.filter(
            estatus='revision',
            tipo_calidad='proveedor',
            piezaRealizada=False
        )

        serializer = self.get_serializer(piezas_pendientes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='piezas_pendientes_revision_dimensional_contador')
    def piezas_pendientes_revision_dimensional_contador(self, request):
        piezas_pendientes = Pieza.objects.filter(
            estatus='revision',
            tipo_calidad='dimensional',
            piezaRealizada=False
        ).count()

        return Response({"cantidad": piezas_pendientes})
    
    @action(detail=False, methods=['get'], url_path='piezas_pendientes_revision_pintura_contador')
    def piezas_pendientes_revision_pintura_contador(self, request):
        piezas_pendientes = Pieza.objects.filter(
            estatus='revision',
            tipo_calidad='pintura',
            piezaRealizada=False
        ).count()

        return Response({"cantidad": piezas_pendientes})
    
    @action(detail=False, methods=['get'], url_path='piezas_pendientes_revision_proveedor_contador')
    def piezas_pendientes_revision_proveedor_contador(self, request):
        piezas_pendientes = Pieza.objects.filter(
            estatus='revision',
            tipo_calidad='proveedor',
            piezaRealizada=False
        ).count()

        return Response({"cantidad": piezas_pendientes})
    
    @action(detail=False, methods=['post'], url_path='obtener_pieza_por_consecutivo')
    def obtener_pieza_por_consecutivo(self, request):
        consecutivo = request.data.get('consecutivo')
        pieza = get_object_or_404(Pieza, consecutivo=consecutivo)
        serializer = self.get_serializer(pieza)
        return Response(serializer.data)
    
    @action(detail=True, methods=['put'], url_path='asignar_procesos_a_usuario')
    def asignar_procesos_a_usuario(self, request, pk=None):
        pieza = self.get_object()
        subprocesos = request.data.get('subprocesos')
        asignado_a_id = request.data.get('asignado_a')

        try:
            usuario = Usuarios.objects.get(id=asignado_a_id)
        except Usuarios.DoesNotExist:
            return Response({"error": "Usuario does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        for subproceso in subprocesos:
            procesos = pieza.procesos.filter(nombre=subproceso)
            if not procesos.exists():
                return Response({"error": f"Subproceso {subproceso} does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            procesos.update(realizadoPor=usuario)

        pieza.refresh_from_db()
        serializer = self.get_serializer(pieza)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='obtener_piezas_subproceso_tiempo')
    def obtener_piezas_subproceso_tiempo(self, request):
        subproceso = request.data.get('subprocesos')
        hora_inicio = request.data.get('hora_inicio')

        if not hora_inicio or not isinstance(hora_inicio, str):
            return Response({"error": "Invalid or missing 'hora_inicio' parameter"}, status=status.HTTP_400_BAD_REQUEST)

        hora_inicio = parse_datetime(hora_inicio)

        piezas = Pieza.objects.filter(
            estatus='aprobado',
            estatusAsignacion=True,
            procesos__nombre__in=subproceso,
            procesos__inicioProceso__date=timezone.now().date(),
            procesos__inicioProceso__time__gte=hora_inicio.time(),
        ).distinct()

        serializer = self.get_serializer(piezas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='obtener_piezas_por_subproceso')
    def obtener_piezas_por_subproceso(self, request):
        subproceso = request.data.get('subprocesos')

        if subproceso is None:
            return Response({"error": "El parámetro 'subprocesos' es requerido"}, status=status.HTTP_400_BAD_REQUEST)

        piezas = Pieza.objects.filter(
            estatus='aprobado',
            estatusAsignacion=True,
            procesos__nombre__in=subproceso,
        ).order_by('-procesos__inicioProceso').distinct()

        serializer = self.get_serializer(piezas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='obtener_piezas_maquina_cnc1')
    def obtener_piezas_maquina_cnc1(self, request):
        return self.obtener_piezas_maquina(request, 'cnc 1')

    @action(detail=False, methods=['get'], url_path='obtener_piezas_maquina_cnc2')
    def obtener_piezas_maquina_cnc2(self, request):
        return self.obtener_piezas_maquina(request, 'cnc 2')

    @action(detail=False, methods=['get'], url_path='obtener_piezas_maquina_fresadora1')
    def obtener_piezas_maquina_fresadora1(self, request):
        return self.obtener_piezas_maquina(request, 'fresadora 1')

    @action(detail=False, methods=['get'], url_path='obtener_piezas_maquina_fresadora2')
    def obtener_piezas_maquina_fresadora2(self, request):
        return self.obtener_piezas_maquina(request, 'fresadora 2')

    @action(detail=False, methods=['get'], url_path='obtener_piezas_maquina_torno')
    def obtener_piezas_maquina_torno(self, request):
        return self.obtener_piezas_maquina(request, 'torno')

    @action(detail=False, methods=['get'], url_path='obtener_piezas_maquina_machueleado')
    def obtener_piezas_maquina_machueleado(self, request):
        return self.obtener_piezas_maquina(request, 'machueleado')

    @action(detail=False, methods=['get'], url_path='obtener_piezas_maquina_limpieza')
    def obtener_piezas_maquina_limpieza(self, request):
        return self.obtener_piezas_maquina(request, 'limpieza')

    @action(detail=False, methods=['get'], url_path='obtener_piezas_maquina_corte')
    def obtener_piezas_maquina_corte(self, request):
        return self.obtener_piezas_maquina(request, 'corte')

    @action(detail=False, methods=['get'], url_path='obtener_piezas_maquina_pintura')
    def obtener_piezas_maquina_pintura(self, request):
        return self.obtener_piezas_maquina(request, 'pintura')

    @action(detail=False, methods=['get'], url_path='obtener_piezas_maquina_pulido')
    def obtener_piezas_maquina_pulido(self, request):
        return self.obtener_piezas_maquina(request, 'pulido')
    
    @action(detail=False, methods=['get'], url_path='obtener_piezas_maquina_cortadoralaser')
    def obtener_piezas_maquina_cortadoralaser(self, request):
        return self.obtener_piezas_maquina(request, 'cortadoralaser')
    
    @action(detail=False, methods=['get'], url_path='obtener_piezas_maquina_dobladora')
    def obtener_piezas_maquina_dobladora(self, request):
        return self.obtener_piezas_maquina(request, 'dobladora')
    
    @action(detail=False, methods=['get'], url_path='obtener_piezas_maquina_machueleadosm')
    def obtener_piezas_maquina_machueleadosm(self, request):
        return self.obtener_piezas_maquina(request, 'machueleadosm')
    
    @action(detail=False, methods=['get'], url_path='obtener_piezas_maquina_limpiezasm')
    def obtener_piezas_maquina_limpiezasm(self, request):
        return self.obtener_piezas_maquina(request, 'limpiezasm')
    
    def obtener_piezas_maquina(self, request, maquina):
        current_time = timezone.now()
        piezas_realizadas = Pieza.objects.filter(
            estatus='aprobado',
            estatusAsignacion=True,
            procesos__maquina=maquina,
            procesos__estatus='realizado',
            procesos__inicioProceso__date=current_time.date(),
        ).distinct()

        piezas_retrasadas = Pieza.objects.filter(
            estatus='aprobado',
            estatusAsignacion=True,
            procesos__maquina=maquina,
            procesos__estatus__in=['pendiente', 'operando'],
            procesos__finProceso__lt=current_time,
        ).distinct()

        total_piezas = piezas_realizadas.count() + piezas_retrasadas.count()
        progreso = piezas_realizadas.count() / total_piezas if total_piezas > 0 else 0

        return Response({
            "progreso": progreso,
            "realizadas": PiezaSerializer(piezas_realizadas, many=True).data,
            "retrasadas": PiezaSerializer(piezas_retrasadas, many=True).data,
        })
    
    @action(detail=False, methods=['get'], url_path='obtener_estadisticas_maquinado_hoy')
    def obtener_estadisticas_maquinado_hoy(self, request):
        current_date = timezone.now().date()
        print(current_date)
        maquinas = ['cnc 1', 'cnc 2', 'fresadora 1', 'fresadora 2', 'torno', 'machueleado', 'limpieza']
        estadisticas = {}

        for maquina in maquinas:
            piezas_realizadas = Pieza.objects.filter(
                estatus='aprobado',
                estatusAsignacion=True,
                procesos__maquina=maquina,
                procesos__estatus='realizado',
                procesos__inicioProceso__date=current_date,
            ).distinct().count()

            piezas_planeadas = Pieza.objects.filter(
                estatus='aprobado',
                estatusAsignacion=True,
                procesos__maquina=maquina,
                procesos__estatus__in=['pendiente', 'operando'],
                procesos__inicioProceso__date=current_date,
            ).distinct().count()

            estadisticas[maquina] = {
                'realizadas': piezas_realizadas,
                'planeado': piezas_planeadas
            }

        return Response(estadisticas)
    
    @action(detail=False, methods=['get'], url_path='obtener_estadisticas_soldadura_hoy')
    def obtener_estadisticas_soldadura_hoy(self, request):
        current_date = timezone.now().date()
        maquinas = ['corte', 'pintura', 'pulido']
        estadisticas = {}

        for maquina in maquinas:
            piezas_realizadas = Pieza.objects.filter(
                estatus='aprobado',
                estatusAsignacion=True,
                procesos__maquina=maquina,
                procesos__estatus='realizado',
                procesos__inicioProceso__date=current_date,
            ).distinct().count()

            piezas_planeadas = Pieza.objects.filter(
                estatus='aprobado',
                estatusAsignacion=True,
                procesos__maquina=maquina,
                procesos__estatus__in=['pendiente', 'operando'],
                procesos__inicioProceso__date=current_date,
            ).distinct().count()

            estadisticas[maquina] = {
                'realizadas': piezas_realizadas,
                'planeado': piezas_planeadas
            }

        return Response(estadisticas)
    
    @action(detail=False, methods=['get'], url_path='obtener_estadisticas_sheetmetal_hoy')
    def obtener_estadisticas_sheetmetal_hoy(self, request):
        current_date = timezone.now().date()
        maquinas = ['cortadora laser', 'dobladora', 'machueleado', 'limpieza'] 
        estadisticas = {}

        for maquina in maquinas:
            piezas_realizadas = Pieza.objects.filter(
                estatus='aprobado',
                estatusAsignacion=True,
                procesos__maquina=maquina,
                procesos__estatus='realizado',
                procesos__inicioProceso__date=current_date,
            ).distinct().count()

            piezas_planeadas = Pieza.objects.filter(
                estatus='aprobado',
                estatusAsignacion=True,
                procesos__maquina=maquina,
                procesos__estatus__in=['pendiente', 'operando'],
                procesos__inicioProceso__date=current_date,
            ).distinct().count()

            estadisticas[maquina] = {
                'realizadas': piezas_realizadas,
                'planeado': piezas_planeadas
            }

        return Response(estadisticas)
    
    @action(detail=False, methods=['get'], url_path='obtener_piezas_actuales')
    def obtener_piezas_actuales(self, request):
        current_time = timezone.now()
        piezas = Pieza.objects.filter(
            estatus='aprobado',
            estatusAsignacion=True,
            procesos__inicioProceso__date=current_time.date(),
            procesos__inicioProceso__lte=current_time,
            procesos__finProceso__gte=current_time,
        ).distinct()

        serializer = self.get_serializer(piezas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='obtener_piezas_actuales_conteo')
    def obtener_piezas_actuales_conteo(self, request):
        current_time = timezone.localtime(timezone.now())
        piezas_count = Pieza.objects.filter(
            estatus='aprobado',
            estatusAsignacion=True,
            procesos__inicioProceso__date=current_time.date(),
            procesos__inicioProceso__lte=current_time,
            procesos__finProceso__gte=current_time,
        ).distinct().count()

        return Response({"piezas_count": piezas_count})
    
    @action(detail=False, methods=['get'], url_path='obtener_piezas_terminadas')
    def obtener_piezas_terminadas(self, request):
        piezas_con_procesos = Pieza.objects.annotate(num_procesos=Count('procesos')).filter(num_procesos__gt=0)

        piezas_terminadas = piezas_con_procesos.annotate(
            num_procesos_realizados=Count('procesos', filter=Q(procesos__estatus='realizado'))
        ).filter(num_procesos=F('num_procesos_realizados'))

        serializer = self.get_serializer(piezas_terminadas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='obtener_piezas_futuras')
    def obtener_piezas_futuras(self, request):
        current_time = timezone.now()
        piezas_futuras = Pieza.objects.filter(
            Q(procesos__inicioProceso__gt=current_time) | Q(procesos__finProceso__gt=current_time)
        ).distinct()

        serializer = self.get_serializer(piezas_futuras, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='piezas_actuales_retrasadas')
    def piezas_actuales_retrasadas(self, request):
        current_time = timezone.now()
        piezas = Pieza.objects.filter(
            estatus='aprobado',
            estatusAsignacion=True,
            procesos__inicioProceso__date=current_time.date(),
            procesos__inicioProceso__lte=current_time,
            procesos__finProceso__lt=current_time,
            procesos__estatus__in=['pendiente', 'operando'],
        ).distinct()

        serializer = self.get_serializer(piezas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='piezas_actuales_retrasadas_conteo')
    def piezas_actuales_retrasadas_conteo(self, request):
        current_time = timezone.now()
        piezas_count = Pieza.objects.filter(
            estatus='aprobado',
            estatusAsignacion=True,
            procesos__inicioProceso__date=current_time.date(),
            procesos__inicioProceso__lte=current_time,
            procesos__finProceso__lt=current_time,
            procesos__estatus__in=['pendiente', 'operando'],
        ).distinct().count()

        return Response({"piezas_count": piezas_count})
    
    @action(detail=False, methods=['get'], url_path='piezas_actuales_prioritarias')
    def piezas_actuales_prioritarias(self, request):
        current_time = timezone.now()
        piezas = Pieza.objects.filter(
            estatus='aprobado',
            estatusAsignacion=True,
            prioridad=True,
            procesos__inicioProceso__date=current_time.date(),
            procesos__inicioProceso__lte=current_time,
            procesos__finProceso__gte=current_time,
        ).distinct()

        serializer = self.get_serializer(piezas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='piezas_actuales_prioritarias_conteo')
    def piezas_actuales_prioritarias_conteo(self, request):
        current_time = timezone.now()
        piezas_count = Pieza.objects.filter(
            estatus='aprobado',
            estatusAsignacion=True,
            prioridad=True,
            procesos__inicioProceso__date=current_time.date(),
            procesos__inicioProceso__lte=current_time,
            procesos__finProceso__gte=current_time,
        ).distinct().count()

        return Response({"piezas_count": piezas_count})
    
    @action(detail=True, methods=['get'], url_path='obtener_piezas_pendientes')
    def obtener_piezas_pendientes(self, request, pk=None):
        pieza = self.get_object()
        total_piezas_placas = pieza.placas.aggregate(Sum('piezas'))['piezas__sum'] or 0
        piezas_pendientes = pieza.piezasTotales - total_piezas_placas
        return Response({"piezas_pendientes": float(piezas_pendientes)})
    
    @action(detail=True, methods=['put'], url_path='asignar_procesos_sin_nesteo')
    def asignar_procesos_sin_nesteo(self, request, pk=None):
        pieza = self.get_object()
        procesos_data = request.data.get('procesos')

        if not procesos_data:
            return Response({"error": "No 'procesos' provided"}, status=status.HTTP_400_BAD_REQUEST)

        for proceso_data in procesos_data:
            proceso_serializer = ProcesoSerializer(data=proceso_data)
            if proceso_serializer.is_valid():
                proceso = proceso_serializer.save()
                pieza.procesos.add(proceso)
            else:
                return Response(proceso_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        pieza.save()

        return Response({"success": f"Procesos have been successfully created and assigned to Pieza {pieza.consecutivo}"}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['put'], url_path='asignar_placa_a_pieza_sin_nesteo')
    def asignar_placa_a_pieza_sin_nesteo(self, request, pk=None):
        pieza = self.get_object()
        pieza.requiere_nesteo = False
        pieza.save()

        return Response({"success": f"Pieza {pieza.consecutivo} has been updated successfully"}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['put'], url_path='asignar_placa_a_pieza/(?P<placa_id>\d+)')
    def asignar_placa_a_pieza(self, request, pk=None, placa_id=None):
        pieza = self.get_object()
        try:
            placa = Placa.objects.get(id=placa_id)
        except Placa.DoesNotExist:
            return Response({"error": "Placa does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        piezas = request.data.get('piezas')
        if piezas is None:
            return Response({"error": "Piezas parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the PiezaPlaca relationship already exists
        try:
            pieza_placa = PiezaPlaca.objects.get(pieza=pieza, placa=placa)
            return Response({"error": "Placa is already associated with this Pieza"}, status=status.HTTP_400_BAD_REQUEST)
        except PiezaPlaca.DoesNotExist:
            # If not, create a new PiezaPlaca relationship
            pieza_placa = PiezaPlaca.objects.create(pieza=pieza, placa=placa, piezas_realizadas=piezas)

        serializer = PiezaSerializer(pieza)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='buscar_piezas_por_material_espesor')
    def buscar_piezas_por_material_espesor(self, request):
        material_nombre = request.data.get('material')
        espesor = request.data.get('espesor')

        if not all([material_nombre, espesor]):
            return Response({"error": "Los parámetros 'material' y 'espesor' son requeridos"}, status=status.HTTP_400_BAD_REQUEST)

        # Inicializa una lista vacía para almacenar las piezas que cumplen con las condiciones
        piezas_validas = []

        # Obtiene todas las piezas
        todas_las_piezas = Pieza.objects.all()

        # Itera sobre todas las piezas
        for pieza in todas_las_piezas:
            # Verifica si la pieza requiere nesteo, tiene un valor en el campo material, y el nombre del material y el espesor coinciden con los proporcionados
            if pieza.requiere_nesteo and pieza.material is not None and pieza.material.nombre == material_nombre and pieza.material.espesor == espesor:
                # Calcula el total de piezas realizadas
                piezas_realizadas = pieza.placas.aggregate(total=Sum('piezaplaca__piezas_realizadas'))['total']

                # Si el total de piezas realizadas es menor que el total de piezas, o si la lista de placas está vacía, añade la pieza a la lista de piezas válidas
                if piezas_realizadas is None or piezas_realizadas < pieza.piezasTotales:
                    piezas_validas.append(pieza)

        # Serializa los objetos Pieza
        piezas_serializer = PiezaSerializer(piezas_validas, many=True)

        return Response(piezas_serializer.data)
    
    @action(detail=True, methods=['post'], url_path='agregar_procesos_a_pieza')
    def agregar_procesos_a_pieza(self, request, pk=None):
        pieza = self.get_object()
        procesos_data = request.data.get('procesos')
        if not procesos_data:
            return Response({"error": "The 'procesos' parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        for proceso_data in procesos_data:
            placa_id = proceso_data.get('placa_id')
            if not placa_id:
                return Response({"error": "The 'placa_id' parameter is required for each proceso"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                placa = Placa.objects.get(id=placa_id)
            except Placa.DoesNotExist:
                return Response({"error": f"Placa with id {placa_id} does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            proceso_data['placa'] = placa.id

            inicioProceso = parse_datetime(proceso_data.get('inicioProceso'))
            finProceso = parse_datetime(proceso_data.get('finProceso'))
            maquina = proceso_data.get('maquina')

            conflictos = Proceso.objects.filter(maquina=maquina, inicioProceso__lt=finProceso, finProceso__gt=inicioProceso).exclude(placa=placa)
            for conflicto in conflictos:
                piezas_conflicto = Pieza.objects.filter(procesos=conflicto, estatusAsignacion=False, estatus="aprobado")
                for pieza_conflicto in piezas_conflicto:
                    inicioProceso_local = timezone.localtime(conflicto.inicioProceso)
                    finProceso_local = timezone.localtime(conflicto.finProceso)
                    if (inicioProceso.day != inicioProceso_local.day or inicioProceso.month != inicioProceso_local.month or inicioProceso.year != inicioProceso_local.year or inicioProceso.hour != inicioProceso_local.hour or inicioProceso.minute != inicioProceso_local.minute or finProceso.day != finProceso_local.day or finProceso.month != finProceso_local.month or finProceso.year != finProceso_local.year or finProceso.hour != finProceso_local.hour or finProceso.minute != finProceso_local.minute):
                        return Response({"error": f"El horario del proceso '{maquina}' no coincide con el horario del proceso '{conflicto.nombre}' en la máquina '{maquina}' que tiene horario de {inicioProceso_local.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]} a {finProceso_local.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}. La placa '{conflicto.placa.nombre}' y la pieza '{pieza_conflicto.consecutivo}'['{pieza_conflicto.id}'] están causando el conflicto. Debe ser exactamente igual.inicioProceso={inicioProceso}, finProceso={finProceso}, conflictoInicioProceso={inicioProceso_local}, conflictoFinProceso={finProceso_local}"}, status=status.HTTP_400_BAD_REQUEST)

            if maquina in ["Laser", "CNC 1", "CNC 2"]:
                cnc_procesos = Proceso.objects.filter(placa=placa, maquina__in=["CNC 1", "CNC 2", "Laser"])
                for cnc_proceso in cnc_procesos:
                    piezas_conflicto = Pieza.objects.filter(procesos=cnc_proceso, estatusAsignacion=False, estatus="aprobado")
                    for pieza_conflicto in piezas_conflicto:
                        inicioProceso_local = timezone.localtime(cnc_proceso.inicioProceso)
                        finProceso_local = timezone.localtime(cnc_proceso.finProceso)
                        if (inicioProceso.day != inicioProceso_local.day or inicioProceso.month != inicioProceso_local.month or inicioProceso.year != inicioProceso_local.year or inicioProceso.hour != inicioProceso_local.hour or inicioProceso.minute != inicioProceso_local.minute or finProceso.day != finProceso_local.day or finProceso.month != finProceso_local.month or finProceso.year != finProceso_local.year or finProceso.hour != finProceso_local.hour or finProceso.minute != finProceso_local.minute):
                            return Response({"error": f"El horario del proceso '{maquina}' no coincide con el horario del proceso '{cnc_proceso.nombre}' en la máquina '{cnc_proceso.maquina}' que tiene horario de {inicioProceso_local.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]} a {finProceso_local.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}. La placa '{cnc_proceso.placa.nombre}' y la pieza '{pieza_conflicto.consecutivo}'['{pieza_conflicto.id}'] están causando el conflicto. Debe ser exactamente igual.inicioProceso={inicioProceso}, finProceso={finProceso}, conflictoInicioProceso={inicioProceso_local}, conflictoFinProceso={finProceso_local}"}, status=status.HTTP_400_BAD_REQUEST)

            proceso_serializer = ProcesoSerializer(data=proceso_data)
            if proceso_serializer.is_valid():
                proceso = proceso_serializer.save()
                pieza.procesos.add(proceso)
            else:
                return Response(proceso_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        pieza.save()

        pieza_serializer = PiezaSerializer(pieza)
        return Response(pieza_serializer.data, status=status.HTTP_200_OK)


# inicioProceso={inicioProceso}, finProceso={finProceso}, conflictoInicioProceso={inicioProceso_local}, conflictoFinProceso={finProceso_local}

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
        total_piezas = Pieza.objects.filter(estatus='aprobado', estatusAsignacion=False).count()
        piezas_aprobadas = Pieza.objects.filter(estatus='aprobado', estatusAsignacion=True).count()
        if total_piezas == 0:
            return Response({"progreso": 100}, status=status.HTTP_200_OK)
        progreso = (piezas_aprobadas / total_piezas) * 100
        return Response({"progreso": progreso}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['put'], url_path='confirmar_produccion_pieza')
    def confirmar_produccion_pieza(self, request, pk=None):
        pieza = self.get_object()
        pieza.estatusAsignacion = True
        pieza.save()
        return Response({"success": f"La Pieza {pieza.consecutivo} ha sido confirmada para producción"}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def progreso_de_piezas_aprobadas(self, request):
        total_piezas = Pieza.objects.all().count()
        piezas_aprobadas = Pieza.objects.filter(estatus='aprobado').count()

        if total_piezas == 0:
            return Response({"error": "No hay Piezas"}, status=status.HTTP_400_BAD_REQUEST)

        progreso = (piezas_aprobadas / total_piezas) * 100
        return Response({"progreso": progreso}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def progreso_de_piezas_con_asignacion_sin_confirmar(self, request):
        total_piezas = Pieza.objects.all().count()
        piezas_con_asignacion_sin_confirmar = Pieza.objects.filter(Q(estatus='aprobado'),
            Q(material__isnull=True) | (Q(placas__isnull=True) & Q(requiere_nesteo=True)) | Q(procesos__isnull=True)).count()

        if total_piezas == 0:
            return Response({"error": "No hay Piezas"}, status=status.HTTP_400_BAD_REQUEST)

        progreso = (piezas_con_asignacion_sin_confirmar / total_piezas) * 100
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
        try:
            ultima_pieza = Pieza.objects.filter(
                Q(estatus='pendiente') | Q(estatus='aprobado'),
                estatusAsignacion=False
            ).latest('fechaCreado')
        except Pieza.DoesNotExist:
            return Response({"detail": "No hay piezas registradas."}, status=404)

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
            Q(estatusAsignacion=False),
            Q(material__isnull=True) | Q(placas__isnull=True) | Q(procesos__isnull=True),
        ).order_by('-fechaCreado').distinct()
        serializer = self.get_serializer(piezas_sin_asignaciones, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def obtener_piezas_sin_procesos(self, request):
        # Obtener todas las piezas que tienen placas
        piezas_con_placas = Pieza.objects.filter(
            Q(placas__isnull=False, requiere_nesteo=True) |
            Q(placas__isnull=True, requiere_nesteo=False),
            material__isnull=False,
            estatus='aprobado',
            estatusAsignacion=False,
        ).distinct()

        # Filtrar las piezas que no tienen procesos asociados a todas las placas
        piezas_sin_procesos = [pieza for pieza in piezas_con_placas if not pieza.todos_procesos_ligados()]

        # Agregar las piezas que no tienen placas, no requieren nesteo y no tienen procesos asociados
        piezas_sin_procesos += [pieza for pieza in Pieza.objects.all() if pieza.sin_placas_procesos()]

        if not piezas_sin_procesos:
            return Response({"message": "No se encontraron piezas sin procesos."})

        serializer = self.get_serializer(piezas_sin_procesos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def obtener_piezas_sin_procesos_numericos(self, request):
        # Obtener todas las piezas que tienen placas
        piezas_con_placas = Pieza.objects.filter(
            Q(placas__isnull=False, requiere_nesteo=True) |
            Q(placas__isnull=True, requiere_nesteo=False),
            material__isnull=False,
            estatus='aprobado',
            estatusAsignacion=False,
        ).distinct()

        # Filtrar las piezas que no tienen la cantidad correcta de procesos asociados a las placas
        piezas_sin_procesos = [pieza for pieza in piezas_con_placas if not pieza.cantidad_correcta_de_procesos()]

        if not piezas_sin_procesos:
            return Response({"message": "No se encontraron piezas sin procesos."})

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
        ).order_by('-fechaCreado').distinct()
        serializer = self.get_serializer(piezas_sin_material_asignado, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def obtener_piezas_terminadas_sin_asignacion_confirmada(self, request):
        # Obtener todas las piezas que tienen placas y procesos
        piezas_con_placas_procesos = Pieza.objects.filter(
            Q(placas__isnull=False, requiere_nesteo=True) |
            Q(placas__isnull=True, requiere_nesteo=False),
            material__isnull=False,
            estatus='aprobado',
            estatusAsignacion=False,
            procesos__isnull=False
        ).distinct()

        # Filtrar las piezas que tienen todos los procesos asociados a todas las placas
        # y que tienen la cantidad correcta de Piezas_realizadas en todas las Placas asociadas
        piezas_terminadas_sin_asignacion_confirmada = [pieza for pieza in piezas_con_placas_procesos if pieza.todos_procesos_ligados() and pieza.piezas_correctas()]

        if not piezas_terminadas_sin_asignacion_confirmada:
            raise NotFound(detail="No se encontraron piezas terminadas sin asignación confirmada.")

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
            Q(material__isnull=True) | (Q(placas__isnull=True) & Q(requiere_nesteo=True)) | Q(procesos__isnull=True)
        ).order_by('-fechaCreado').distinct()[:5]
        serializer = PiezaSerializer(piezas_pendientes_de_asignar, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def ultimas_piezas_pendientes_de_confirmar(self, request):
        piezas_pendientes_de_confirmar = Pieza.objects.filter(
            Q(estatus='aprobado'),
            Q(material__isnull=False),
            Q(placas__isnull=False) | Q(requiere_nesteo=False),
            Q(procesos__isnull=False),
            Q(estatusAsignacion=False)
        ).order_by('-fechaCreado').distinct()[:5]
        serializer = PiezaSerializer(piezas_pendientes_de_confirmar, many=True)
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