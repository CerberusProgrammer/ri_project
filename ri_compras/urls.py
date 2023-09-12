from django.urls import path
from . import views

urlpatterns = [
    path('usuarios/crear/', views.crear_usuario, name='crear-usuario'),
]
