from rest_framework import viewsets
from .models import Departamento, Usuarios
from .serializer import DepartamentoSerializer, UsuariosSerializer
from rest_framework import filters

class DepartamentoViewSet(viewsets.ModelViewSet):
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer

class UsuariosViewSet(viewsets.ModelViewSet):
    queryset = Usuarios.objects.all()
    serializer_class = UsuariosSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['departamento__nombre'] # usuarios?search=""
    ordering_fields = ['username'] # usuarios?ordering=username