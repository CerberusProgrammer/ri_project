from rest_framework import serializers
from ri_compras.models import Usuarios
from ri_compras.serializer import SimpleUsuariosSerializer
from .models import Material, Notificacion, Placa, Proceso, Pieza, PiezaPlaca

class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = '__all__'

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'

class PlacaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Placa
        fields = '__all__'

class ProcesoSerializer(serializers.ModelSerializer):
    placa = serializers.PrimaryKeyRelatedField(queryset=Placa.objects.all(), write_only=True, required=False)
    placa_detail = PlacaSerializer(source='placa', read_only=True)
    realizadoPor = SimpleUsuariosSerializer(read_only=True)

    class Meta:
        model = Proceso
        fields = '__all__'

class PiezaPlacaSerializer(serializers.ModelSerializer):
    placa = PlacaSerializer()

    class Meta:
        model = PiezaPlaca
        fields = ['placa', 'piezas_realizadas']

class PiezaSerializer(serializers.ModelSerializer):
    material = MaterialSerializer(many=False, read_only=True)
    placas = PiezaPlacaSerializer(source='piezaplaca_set', many=True, read_only=True)
    procesos = ProcesoSerializer(many=True, read_only=True)
    creadoPor = SimpleUsuariosSerializer(read_only=True)
    creadoPorId = serializers.PrimaryKeyRelatedField(source='creadoPor', queryset=Usuarios.objects.all(), write_only=True)

    class Meta:
        model = Pieza
        fields = '__all__'