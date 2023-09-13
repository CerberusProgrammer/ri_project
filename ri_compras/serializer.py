from rest_framework import serializers
from .models import Departamento
from .models import Usuarios
from .models import Producto
from .models import Componente

class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = ['id', 'nombre', 'presupuesto']

class UsuariosSerializer(serializers.ModelSerializer):
    departamento = DepartamentoSerializer(read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuarios
        fields = ['id', 'username', 'nombre', 'telefono', 'correo', 'rol', 'is_staff', 'departamento', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuarios.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password is not None:
            user.set_password(password)
            user.save()
        return user

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'descripcion', 'cantidad', 'precio']

class ComponenteSerializer(serializers.ModelSerializer):
    material = ProductoSerializer(many=True, read_only=True)

    class Meta:
        model = Componente
        fields = ['id', 'nombre', 'descripcion', 'material', 'cantidad', 'precio']