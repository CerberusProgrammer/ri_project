from django.urls import path
from django.urls import include
from rest_framework.routers import DefaultRouter
from .views import DepartamentoViewSet
from .views import UsuariosViewSet
from .views import ProductoViewSet
from .views import ComponenteViewSet

router = DefaultRouter()
router.register(r'departamentos', DepartamentoViewSet)
router.register(r'usuarios', UsuariosViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'componentes', ComponenteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]