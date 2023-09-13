from django.contrib import admin
from .models import Usuarios
from .models import Departamento
from .models import Producto
from .models import Componente

admin.site.register(Usuarios)
admin.site.register(Departamento)
admin.site.register(Producto)
admin.site.register(Componente)