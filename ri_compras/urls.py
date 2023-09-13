from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartamentoViewSet, UsuariosViewSet

router = DefaultRouter()
router.register(r'departamentos', DepartamentoViewSet)
router.register(r'usuarios', UsuariosViewSet)

urlpatterns = [
    path('', include(router.urls)),
]