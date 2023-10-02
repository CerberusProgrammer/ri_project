from rest_framework import serializers
from .models import Departamento
from .models import Usuarios
from .models import Producto
from .models import Servicio
from .models import Requisicion
from .models import Proveedor
from .models import OrdenDeCompra
from .models import Recibo
from .models import Project

class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = ['id', 'nombre', 'presupuesto']

class UsuariosSerializer(serializers.ModelSerializer):
    departamento = DepartamentoSerializer(read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuarios
        fields = ['id', 'username', 'nombre', 'telefono', 'correo', 'rol', 'departamento', 'requisiciones', 'password']
        read_only_fields = ['requisiciones'] 

    def validate_departamento(self, value):
        if not value:
            raise serializers.ValidationError("El departamento es obligatorio")
        return value

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

class ProjectSerializer(serializers.ModelSerializer):
    usuario = UsuariosSerializer(read_only=True)
    
    class Meta:
        model = Project
        fields = '__all__'

class RequisicionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requisicion
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'descripcion', 'cantidad', 'costo', 'identificador', 'divisa']

class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ['id', 'nombre', 'descripcion', 'costo', 'divisa']

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ['id', 'nombre', 'direccion', 'telefono', 'correo', 'pagina','calidad', 'tiempo_de_entegra_estimado']

class OrdenDeCompraSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)
    proveedor = ProveedorSerializer(read_only=True)
    requisiciones = RequisicionSerializer(many=True, read_only=True)

    class Meta:
        model = OrdenDeCompra
        fields = ['id', 'fecha_emision', 'proveedor', 'total', 'requisiciones', 'usuario']

class ReciboSerializer(serializers.ModelSerializer):
    orden = OrdenDeCompraSerializer(many=True)

    class Meta:
        model = Recibo
        fields = ['orden', 'estado', 'descripcion']