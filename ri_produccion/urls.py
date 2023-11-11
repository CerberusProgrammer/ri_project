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
    path('piezas/pendientes/', PiezaViewSet.as_view({'get': 'piezas_pendientes'})),
    path('piezas/prioridad/', PiezaViewSet.as_view({'get': 'piezas_prioridad'})),
    path('piezas/proxima/', PiezaViewSet.as_view({'get': 'proxima_pieza'})),
    path('piezas/hoy/', PiezaViewSet.as_view({'get': 'piezas_hoy'})),
    path('procesos/mis-procesos/', ProcesoViewSet.as_view({'get': 'mis_procesos'})),
    path('piezas/porcentaje-realizadas-hoy/', PiezaViewSet.as_view({'get': 'porcentaje_realizadas_hoy'})),
    path('procesos/porcentaje-realizados-hoy/', ProcesoViewSet.as_view({'get': 'porcentaje_realizados_hoy'})),
    path('procesos/usuario-mas-rapido/', ProcesoViewSet.as_view({'get': 'usuario_mas_rapido'})),
    path('procesos/usuario-mas-procesos/', ProcesoViewSet.as_view({'get': 'usuario_mas_procesos'})),
]
