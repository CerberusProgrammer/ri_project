from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MaterialViewSet, NotificacionViewSet, PlacaViewSet, ProcesoViewSet, PiezaViewSet

router = DefaultRouter()
router.register(r'materiales', MaterialViewSet)
router.register(r'placas', PlacaViewSet)
router.register(r'procesos', ProcesoViewSet)
router.register(r'piezas', PiezaViewSet)
router.register(r'notificaciones', NotificacionViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
