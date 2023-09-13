from django.contrib import admin
from .models import Usuarios
from .models import Departamento
from .models import Producto
from .models import Componente
from .models import Servicio
from .models import Requisicion
from .models import Proveedor
from .models import OrdenDeCompra

admin.site.register(Usuarios)
admin.site.register(Departamento)
admin.site.register(Producto)
admin.site.register(Componente)
admin.site.register(Servicio)
admin.site.register(Requisicion)
admin.site.register(Proveedor)
admin.site.register(OrdenDeCompra)