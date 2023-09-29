from django.urls import path
from django.urls import include
from rest_framework.routers import DefaultRouter
from .views import DepartamentoViewSet
from .views import UsuariosViewSet
from .views import ProductoViewSet
from .views import RequisicionViewSet
from .views import ProveedorViewSet
from .views import OrdenDeCompraViewSet
from .views import ReciboViewSet
from .views import ServicioViewSet
from .views import CustomObtainAuthToken
from .views import GetUserFromToken
from .views import ProjectViewSet

router = DefaultRouter()
router.register(r'departamentos', DepartamentoViewSet)
router.register(r'usuarios', UsuariosViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'servicios', ServicioViewSet)
router.register(r'requisiciones', RequisicionViewSet)
router.register(r'proveedores', ProveedorViewSet)
router.register(r'ordenes', OrdenDeCompraViewSet)
router.register(r'recibos', ReciboViewSet)
router.register(r'proyectos', ProjectViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('login/', CustomObtainAuthToken.as_view(), name='login'),
    path('loginbytoken/', GetUserFromToken.as_view(), name='loginbytoken'),
]