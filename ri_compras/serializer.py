from rest_framework import serializers
from .models import Departamento, ProductoRequisicion, ServicioRequisicion
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

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'descripcion', 'cantidad', 'costo', 'identificador', 'divisa']

class SimpleUserProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuarios
        fields = ['id', 'username', 'nombre', 'telefono', 'correo', 'rol']

class SimpleProjectSerializer(serializers.ModelSerializer):
    usuario = SimpleUserProjectSerializer(read_only=True)
    
    class Meta:
        model = Project
        fields = ['id', 'nombre', 'descripcion', 'usuario']

class SimpleProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ['id', 'nombre', 'direccion', 'telefono', 'correo', 'pagina', 'calidad', 'tiempo_de_entegra_estimado']

class SimpleServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ['id', 'nombre', 'descripcion', 'costo', 'divisa']

class ProductoTokenRequisicionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoRequisicion
        fields = '__all__'

class SimpleRequisicionSerializer(serializers.ModelSerializer):
    proyecto = SimpleProjectSerializer(read_only=True)
    proveedor = SimpleProveedorSerializer(read_only=True)
    productos = ProductoTokenRequisicionSerializer(source='productorequisicion_set', many=True, read_only=True)
    servicios = SimpleServicioSerializer(source='serviciorequisicion_set', many=True, read_only=True)
    usuario = SimpleUserProjectSerializer(read_only=True)

    class Meta:
        model = Requisicion
        fields = ['id', 'proyecto', 'proveedor', 'productos', 'fecha_creacion', 'motivo', 'total', 'aprobado', 'usuario']

class UsuariosSerializer(serializers.ModelSerializer):
    requisiciones = SimpleRequisicionSerializer(many=True, read_only=True)
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

class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ['id', 'nombre', 'descripcion', 'costo', 'divisa']

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ['id', 'nombre', 'direccion', 'telefono', 'correo', 'pagina','calidad', 'tiempo_de_entegra_estimado']

class SimpleUsuariosSerializer(serializers.ModelSerializer):
    departamento = DepartamentoSerializer(read_only=True)

    class Meta:
        model = Usuarios
        fields = ['id', 'username', 'nombre', 'telefono', 'correo', 'rol', 'departamento']

class ProductoRequisicionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoRequisicion
        fields = '__all__'

class RequisicionSerializer(serializers.ModelSerializer):
    usuario = SimpleUsuariosSerializer(read_only=True)
    usuario_id = serializers.IntegerField(write_only=True)
    proyecto = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    proveedor = serializers.PrimaryKeyRelatedField(queryset=Proveedor.objects.all())
    productos = ProductoRequisicionSerializer(source='productorequisicion_set', many=True, read_only=True)

    class Meta:
        model = Requisicion
        fields = '__all__'

    def create(self, validated_data):
        usuario_id = validated_data.pop('usuario_id')
        validated_data['usuario'] = Usuarios.objects.get(id=usuario_id)
        productos_data = validated_data.pop('productos', [])
        servicios_data = validated_data.pop('servicios', [])
        requisicion = Requisicion.objects.create(**validated_data)

        for producto_data in productos_data:
            ProductoRequisicion.objects.create(requisicion=requisicion, **producto_data)

        for servicio_data in servicios_data:
            ServicioRequisicion.objects.create(requisicion=requisicion, **servicio_data)

        return requisicion

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['usuario'] = UsuariosSerializer(instance.usuario).data
        representation['proyecto'] = ProjectSerializer(instance.proyecto).data
        representation['proveedor'] = ProveedorSerializer(instance.proveedor).data
        return representation

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