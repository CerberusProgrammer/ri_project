from rest_framework import serializers
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
    placa = PlacaSerializer()
    class Meta:
        model = Proceso
        fields = '__all__'

class PiezaSerializer(serializers.ModelSerializer):
    material = serializers.PrimaryKeyRelatedField(queryset=Material.objects.all(), required=False)
    placas = serializers.PrimaryKeyRelatedField(queryset=Placa.objects.all(), many=True, required=False)
    procesos = serializers.PrimaryKeyRelatedField(queryset=Proceso.objects.all(), many=True, required=False)

    class Meta:
        model = Pieza
        fields = ['consecutivo', 'ordenCompra', 'piezas', 'piezasTotales', 'material', 'placas', 'procesos', 'creadoPor', 'archivo_pdf']

