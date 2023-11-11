from rest_framework import viewsets, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Min, Max

from ri_compras.models import Usuarios

from .models import Material, Placa, Proceso, Pieza
from .serializers import MaterialSerializer, PlacaSerializer, ProcesoSerializer, PiezaSerializer

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'espesor', 'proveedor']
    ordering_fields = ['nombre', 'espesor']

class PlacaViewSet(viewsets.ModelViewSet):
    queryset = Placa.objects.all()
    serializer_class = PlacaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['piezas']
    ordering_fields = ['piezas']

class ProcesoViewSet(viewsets.ModelViewSet):
    queryset = Proceso.objects.all()
    serializer_class = ProcesoSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'estatus', 'maquina']
    ordering_fields = ['nombre', 'estatus', 'maquina']
    
    def porcentaje_realizados_hoy(self, request):
        procesos_hoy = [proceso for proceso in Proceso.objects.all() if proceso.inicioProceso.date() == timezone.now().date()]

        procesos_realizados_hoy = [proceso for proceso in procesos_hoy if proceso.estatus == 'realizado']

        porcentaje_realizados_hoy = len(procesos_realizados_hoy) / len(procesos_hoy) * 100 if procesos_hoy else 0

        return Response({"porcentaje_realizados_hoy": porcentaje_realizados_hoy})
    
    def mis_procesos(self, request):
        mis_procesos = Proceso.objects.filter(realizadoPor=request.user)

        if not mis_procesos:
            return Response({"message": "No has realizado ningún proceso."})

        serializer = self.get_serializer(mis_procesos, many=True)
        return Response(serializer.data)
    
    def usuario_mas_procesos(self, request):
        usuario_mas_procesos = Usuarios.objects.annotate(num_procesos=Count('proceso')).order_by('-num_procesos').first()

        if not usuario_mas_procesos:
            return Response({"message": "No hay ningún usuario que haya realizado un proceso."})

        serializer = self.get_serializer(usuario_mas_procesos)
        return Response(serializer.data)

    def usuario_mas_rapido(self, request):
        usuario_mas_rapido = Usuarios.objects.annotate(duracion_proceso=Min('proceso__finProceso') - Max('proceso__inicioProceso')).order_by('duracion_proceso').first()

        if not usuario_mas_rapido:
            return Response({"message": "No hay ningún usuario que haya realizado un proceso."})

        serializer = self.get_serializer(usuario_mas_rapido)
        return Response(serializer.data)

class PiezaViewSet(viewsets.ModelViewSet):
    queryset = Pieza.objects.all()
    serializer_class = PiezaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['consecutivo', 'ordenCompra']
    ordering_fields = ['consecutivo', 'ordenCompra']
    
    def piezas_pendientes(self, request):
        piezas_pendientes = Pieza.objects.filter(procesos__estatus='pendiente')
        serializer = self.get_serializer(piezas_pendientes, many=True)
        return Response(serializer.data)

    def piezas_prioridad(self, request):
        piezas_prioridad = Pieza.objects.filter(prioridad=True)
        serializer = self.get_serializer(piezas_prioridad, many=True)
        return Response(serializer.data)

    def piezas_hoy(self, request):
        piezas_hoy = [pieza for pieza in Pieza.objects.all() if any(proceso.inicioProceso.date() == timezone.now().date() for proceso in pieza.procesos.all())]

        if not piezas_hoy:
            return Response({"message": "No hay ninguna pieza con un proceso que comienza hoy."})

        serializer = self.get_serializer(piezas_hoy, many=True)
        return Response(serializer.data)
    
    def proxima_pieza(self, request):
        piezas_proximas = [pieza for pieza in Pieza.objects.all() if any(proceso.inicioProceso > timezone.now() for proceso in pieza.procesos.all())]

        if not piezas_proximas:
            return Response({"message": "No hay ninguna pieza con un próximo proceso a realizar."})

        proxima_pieza = min(piezas_proximas, key=lambda pieza: min(proceso.inicioProceso for proceso in pieza.procesos.all() if proceso.inicioProceso > timezone.now()))

        serializer = self.get_serializer(proxima_pieza)
        return Response(serializer.data)
    
    def porcentaje_realizadas_hoy(self, request):
        piezas_hoy = [pieza for pieza in Pieza.objects.all() if any(proceso.inicioProceso.date() == timezone.now().date() for proceso in pieza.procesos.all())]

        piezas_realizadas_hoy = [pieza for pieza in piezas_hoy if all(proceso.estatus == 'realizado' for proceso in pieza.procesos.all())]

        porcentaje_realizadas_hoy = len(piezas_realizadas_hoy) / len(piezas_hoy) * 100 if piezas_hoy else 0

        return Response({"porcentaje_realizadas_hoy": porcentaje_realizadas_hoy})
