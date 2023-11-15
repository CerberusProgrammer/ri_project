from rest_framework import serializers
from ri_compras.models import Usuarios

from ri_compras.serializer import SimpleUsuariosSerializer
from .models import Material, Placa, Proceso, Pieza

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'

class PlacaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Placa
        fields = '__all__'

class ProcesoSerializer(serializers.ModelSerializer):
    placa = PlacaSerializer(read_only=True)
    class Meta:
        model = Proceso
        fields = '__all__'

class PiezaSerializer(serializers.ModelSerializer):
    material = serializers.PrimaryKeyRelatedField(queryset=Material.objects.all(), required=False)
    placas = serializers.PrimaryKeyRelatedField(queryset=Placa.objects.all(), many=True, required=False)
    procesos = ProcesoSerializer(many=True, read_only=True)
    creadoPor = SimpleUsuariosSerializer(read_only=True)
    creadoPorId = serializers.PrimaryKeyRelatedField(source='creadoPor', queryset=Usuarios.objects.all(), write_only=True)  # For POST requests

    class Meta:
        model = Pieza
        fields = '__all__'
