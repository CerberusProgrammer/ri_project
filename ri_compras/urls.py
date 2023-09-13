from django.urls import path
from django.urls import include
from rest_framework.routers import DefaultRouter
from .views import DepartamentoViewSet
from .views import UsuariosViewSet

router = DefaultRouter()
router.register(r'departamentos', DepartamentoViewSet)
router.register(r'usuarios', UsuariosViewSet)

urlpatterns = [
    path('', include(router.urls)),
]