from rest_framework import viewsets
from .models import Departamento
from .models import Usuarios
from .models import Producto
from .models import Componente
from .serializer import DepartamentoSerializer
from .serializer import UsuariosSerializer
from .serializer import ProductoSerializer
from .serializer import ComponenteSerializer
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
    
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

class ComponenteViewSet(viewsets.ModelViewSet):
    queryset = Componente.objects.all()
    serializer_class = ComponenteSerializer