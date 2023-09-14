from django.contrib import admin
from django.urls import path, include

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="API de RI Compras",
        default_version='v1',
        description="Documentación Oficial de la API de RI Compras",
        terms_of_service="no avaible",
        contact=openapi.Contact(email="cerberusprogrammer@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('ri_compras.urls')),
    path('api/doc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]