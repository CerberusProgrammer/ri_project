from django.contrib import admin
from .models import Estante, Message, Pedido, ProductoAlmacen, ProductoRequisicion, Rack, ProductoRequisicion, Usuarios
from .models import Departamento
from .models import Producto
from .models import Servicio
from .models import Requisicion
from .models import Proveedor
from .models import OrdenDeCompra
from .models import Recibo
from .models import Project
from .models import Contacto
from simple_history.admin import SimpleHistoryAdmin

class ProjectAdmin(SimpleHistoryAdmin):
    def history_view(self, request, object_id, extra_context=None):
        object = self.model.objects.get(pk=object_id)
        history = object.history.all()
        
        return super().history_view(request, object_id, extra_context=extra_context)

    def get_change_reason(self):
        return None

admin.site.register(Project, ProjectAdmin)

class ProductosAdmin(SimpleHistoryAdmin):
    def history_view(self, request, object_id, extra_context=None):
        object = self.model.objects.get(pk=object_id)
        history = object.history.all()

        return super().history_view(request, object_id, extra_context=extra_context)

admin.site.register(Producto, ProductosAdmin)

class ProductosRequisicionAdmin(SimpleHistoryAdmin):
    def history_view(self, request, object_id, extra_context=None):
        object = self.model.objects.get(pk=object_id)
        history = object.history.all()

        return super().history_view(request, object_id, extra_context=extra_context)

admin.site.register(ProductoRequisicion, ProductosRequisicionAdmin)

class PedidosAdmin(SimpleHistoryAdmin):
    def history_view(self, request, object_id, extra_context=None):
        object = self.model.objects.get(pk=object_id)
        history = object.history.all()

        return super().history_view(request, object_id, extra_context=extra_context)

admin.site.register(Pedido, PedidosAdmin)

class ProductosAlmacenAdmin(SimpleHistoryAdmin):
    def history_view(self, request, object_id, extra_context=None):
        object = self.model.objects.get(pk=object_id)
        history = object.history.all()

        return super().history_view(request, object_id, extra_context=extra_context)

admin.site.register(ProductoAlmacen, ProductosAlmacenAdmin)

class RackAdmin(SimpleHistoryAdmin):
    def history_view(self, request, object_id, extra_context=None):
        object = self.model.objects.get(pk=object_id)
        history = object.history.all()

        return super().history_view(request, object_id, extra_context=extra_context)

admin.site.register(Rack, RackAdmin)

class EstanteAdmin(SimpleHistoryAdmin):
    def history_view(self, request, object_id, extra_context=None):
        object = self.model.objects.get(pk=object_id)
        history = object.history.all()

        return super().history_view(request, object_id, extra_context=extra_context)

admin.site.register(Estante, EstanteAdmin)

class UsuariosAdmin(SimpleHistoryAdmin):
    def history_view(self, request, object_id, extra_context=None):
        object = self.model.objects.get(pk=object_id)
        history = object.history.all()

        return super().history_view(request, object_id, extra_context=extra_context)

admin.site.register(Usuarios, UsuariosAdmin)

class DepartamentoAdmin(SimpleHistoryAdmin):
    def history_view(self, request, object_id, extra_context=None):
        object = self.model.objects.get(pk=object_id)
        history = object.history.all()

        return super().history_view(request, object_id, extra_context=extra_context)

admin.site.register(Departamento, DepartamentoAdmin)

class ServicioAdmin(SimpleHistoryAdmin):
    def history_view(self, request, object_id, extra_context=None):
        object = self.model.objects.get(pk=object_id)
        history = object.history.all()

        return super().history_view(request, object_id, extra_context=extra_context)

admin.site.register(Servicio, ServicioAdmin)

class RequisicionAdmin(SimpleHistoryAdmin):
    def history_view(self, request, object_id, extra_context=None):
        object = self.model.objects.get(pk=object_id)
        history = object.history.all()

        return super().history_view(request, object_id, extra_context=extra_context)

admin.site.register(Requisicion, RequisicionAdmin)

class ContactoInline(admin.TabularInline):
    model = Proveedor.contactos.through

class ProveedorAdmin(SimpleHistoryAdmin):
    inlines = [
        ContactoInline,
    ]
    exclude = ('contactos',)
    
    def history_view(self, request, object_id, extra_context=None):
        object = self.model.objects.get(pk=object_id)
        history = object.history.all()

        return super().history_view(request, object_id, extra_context=extra_context)

admin.site.register(Proveedor, ProveedorAdmin)

class OrdenDeCompraAdmin(SimpleHistoryAdmin):
    def history_view(self, request, object_id, extra_context=None):
        object = self.model.objects.get(pk=object_id)
        history = object.history.all()

        return super().history_view(request, object_id, extra_context=extra_context)

admin.site.register(OrdenDeCompra, OrdenDeCompraAdmin)

class ReciboAdmin(SimpleHistoryAdmin):
    def history_view(self, request, object_id, extra_context=None):
        object = self.model.objects.get(pk=object_id)
        history = object.history.all()

        return super().history_view(request, object_id, extra_context=extra_context)

admin.site.register(Recibo, ReciboAdmin)
admin.site.register(Contacto)

class MessageAdmin(SimpleHistoryAdmin):
    def history_view(self, request, object_id, extra_context=None):
        object = self.model.objects.get(pk=object_id)
        history = object.history.all()

        return super().history_view(request, object_id, extra_context=extra_context)

admin.site.register(Message, MessageAdmin)