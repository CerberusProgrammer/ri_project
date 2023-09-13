from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UsuariosViewSet

router = DefaultRouter()
router.register(r'users', UsuariosViewSet, basename='user')

urlpatterns = [
    path('api/users/', UsuariosViewSet.as_view({'post': 'create'}), name='create_user'),
    path('api/users/details/', UsuariosViewSet.as_view({'get': 'details'}), name='get_user_details'),
    path('api/users/update_user/', UsuariosViewSet.as_view({'put': 'update_user'}), name='update_user'),
]

urlpatterns += router.urls