from django.urls import path
from django.urls import include
from rest_framework.routers import DefaultRouter
from .views import DepartamentoViewSet
from .views import UsuariosViewSet
from .views import ProductoViewSet
from .views import ComponenteViewSet
from .views import RequisicionViewSet
from .views import ProveedorViewSet
from .views import OrdenDeCompraViewSet
from .views import ReciboViewSet

router = DefaultRouter()
router.register(r'departamentos', DepartamentoViewSet)
router.register(r'usuarios', UsuariosViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'componentes', ComponenteViewSet)
router.register(r'requisiciones', RequisicionViewSet)
router.register(r'proveedores', ProveedorViewSet)
router.register(r'ordenesdecompras', OrdenDeCompraViewSet)
router.register(r'recibos', ReciboViewSet)

urlpatterns = [
    path('', include(router.urls)),
]