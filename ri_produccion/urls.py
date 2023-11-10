from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MaterialViewSet, PlacaViewSet, ProcesoViewSet, PiezaViewSet

router = DefaultRouter()
router.register(r'materiales', MaterialViewSet)
router.register(r'placas', PlacaViewSet)
router.register(r'procesos', ProcesoViewSet)
router.register(r'piezas', PiezaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
