from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Material, Placa, Proceso, Pieza

class MaterialAdmin(SimpleHistoryAdmin):
    def history_view(self, request, object_id, extra_context=None):
        object = self.model.objects.get(pk=object_id)
        history = object.history.all()
        return super().history_view(request, object_id, extra_context=extra_context)

admin.site.register(Material, MaterialAdmin)

class PlacaAdmin(SimpleHistoryAdmin):
    def history_view(self, request, object_id, extra_context=None):
        object = self.model.objects.get(pk=object_id)
        history = object.history.all()
        return super().history_view(request, object_id, extra_context=extra_context)

admin.site.register(Placa, PlacaAdmin)

class ProcesoAdmin(SimpleHistoryAdmin):
    def history_view(self, request, object_id, extra_context=None):
        object = self.model.objects.get(pk=object_id)
        history = object.history.all()
        return super().history_view(request, object_id, extra_context=extra_context)

admin.site.register(Proceso, ProcesoAdmin)

class PiezaAdmin(SimpleHistoryAdmin):
    def history_view(self, request, object_id, extra_context=None):
        object = self.model.objects.get(pk=object_id)
        history = object.history.all()
        return super().history_view(request, object_id, extra_context=extra_context)

admin.site.register(Pieza, PiezaAdmin)
