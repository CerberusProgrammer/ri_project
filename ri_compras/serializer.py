from rest_framework import serializers
from .models import Contacto
from .models import ServicioRequisicion
from .models import Departamento
from .models import Message
from .models import ProductoRequisicion
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
        fields = ['id', 'nombre', 'descripcion', 'presupuesto','divisa']

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

class ContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacto
        fields = '__all__'

class SimpleUserProjectSerializer(serializers.ModelSerializer):
    departamento = DepartamentoSerializer()
    
    class Meta:
        model = Usuarios
        fields = ['id', 'username', 'nombre', 'telefono', 'correo', 'rol', 'departamento']

class SimpleProjectSerializer(serializers.ModelSerializer):
    usuario = SimpleUserProjectSerializer(read_only=True)
    
    class Meta:
        model = Project
        fields = ['id', 'nombre', 'descripcion', 'usuario']

class SimpleProveedorSerializer(serializers.ModelSerializer):
    contactos = ContactoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Proveedor
        fields = '__all__'

class SimpleServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ['id', 'nombre', 'descripcion', 'costo', 'divisa']

class SimpleRequisicionSerializer(serializers.ModelSerializer):
    usuario = SimpleUserProjectSerializer()
    proyecto = SimpleProjectSerializer(read_only=True)
    proveedor = SimpleProveedorSerializer(read_only=True)
    productos = ProductoSerializer(many=True, read_only=True)
    servicios = SimpleServicioSerializer(many=True, read_only=True)

    class Meta:
        model = Requisicion
        fields = ['id', 'usuario', 'proyecto', 'proveedor', 'productos', 'servicios', 'fecha_creacion', 'fecha_aprobado', 'fecha_entrega_estimada', 'motivo', 'total', 'aprobado','ordenado', 'archivo_pdf']

class UserMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuarios
        fields = ['id', 'username', 'nombre', 'telefono', 'correo']

class MessageSerializer(serializers.ModelSerializer):
    user = UserMessageSerializer(read_only=True)
    from_user = UserMessageSerializer(read_only=True)

    class Meta:
        model = Message
        fields = '__all__'

    def create(self, validated_data):
        user_id = self.context['request'].data.get('user')
        from_user_id = self.context['request'].data.get('from_user')

        user = Usuarios.objects.get(id=user_id)
        from_user = Usuarios.objects.get(id=from_user_id)

        message = Message.objects.create(
            user=user,
            from_user=from_user,
            title=validated_data.get('title'),
            message=validated_data.get('message')
        )

        return message

class UsuariosSerializer(serializers.ModelSerializer):
    requisiciones = SimpleRequisicionSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    departamento = DepartamentoSerializer(read_only=True)
    password = serializers.CharField(write_only=True)
    proyectos = SimpleProjectSerializer(many=True, read_only=True)

    class Meta:
        model = Usuarios
        fields = ['id', 'username', 'nombre', 'telefono', 'correo', 'rol', 'departamento', 'requisiciones', 'password', 'messages', 'proyectos']
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

class UsuariosVerySimpleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Usuarios
        fields = ['id', 'username', 'nombre', 'telefono', 'correo', 'rol']

class ProjectSerializer(serializers.ModelSerializer):
    usuario = UsuariosVerySimpleSerializer(read_only=True)
    
    class Meta:
        model = Project
        fields = '__all__'

class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ['id', 'nombre', 'descripcion', 'costo', 'divisa']

class ProveedorSerializer(serializers.ModelSerializer):
    contactos = ContactoSerializer(many=True)

    class Meta:
        model = Proveedor
        fields = '__all__'

    def create(self, validated_data):
        contactos_data = validated_data.pop('contactos')
        proveedor = Proveedor.objects.create(**validated_data)
        for contacto_data in contactos_data:
            contacto = Contacto.objects.create(**contacto_data)
            proveedor.contactos.add(contacto)
        return proveedor

    def update(self, instance, validated_data):
        contactos_data = validated_data.pop('contactos')
        instance = super().update(instance, validated_data)

        for contacto_data in contactos_data:
            contacto_id = contacto_data.get('id', None)
            if contacto_id:
                # update existing contact
                Contacto.objects.filter(id=contacto_id).update(**contacto_data)
            else:
                # create new contact
                contacto = Contacto.objects.create(**contacto_data)
                instance.contactos.add(contacto)

        return instance


class SimpleUsuariosSerializer(serializers.ModelSerializer):
    departamento = DepartamentoSerializer(read_only=True)

    class Meta:
        model = Usuarios
        fields = ['id', 'username', 'nombre', 'telefono', 'correo', 'rol', 'departamento']

class SimpleOrdenDeCompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdenDeCompra
        fields = ['id', 'fecha_emision', 'estado']  # Solo los campos que necesitas


class RequisicionSerializer(serializers.ModelSerializer):
    usuario = SimpleUserProjectSerializer(read_only=True)
    usuario_id = serializers.IntegerField(write_only=True)
    proyecto = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), allow_null=True)
    proveedor = serializers.PrimaryKeyRelatedField(queryset=Proveedor.objects.all())
    productos = ProductoSerializer(many=True)
    servicios = ServicioSerializer(many=True)
    ordenes = serializers.SerializerMethodField()

    class Meta:
        model = Requisicion
        fields = '__all__'
    
    def get_ordenes(self, obj):
        ordenes = OrdenDeCompra.objects.filter(requisicion=obj)
        return SimpleOrdenDeCompraSerializer(ordenes, many=True).data

    def create(self, validated_data):
        archivo_pdf = validated_data.pop('archivo_pdf', None)
        usuario_id = validated_data.pop('usuario_id')
        validated_data['usuario'] = Usuarios.objects.get(id=usuario_id)
        productos_data = validated_data.pop('productos', [])
        servicios_data = validated_data.pop('servicios', [])
        requisicion = Requisicion.objects.create(**validated_data)

        for producto_data in productos_data:
            producto, created = ProductoRequisicion.objects.get_or_create(**producto_data)
            requisicion.productos.add(producto)

        for servicio_data in servicios_data:
            servicio, created = ServicioRequisicion.objects.get_or_create(**servicio_data)
            requisicion.servicios.add(servicio)

        if archivo_pdf is not None:
            requisicion.archivo_pdf = archivo_pdf
            requisicion.save()

        return requisicion

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['usuario'] = SimpleUserProjectSerializer(instance.usuario).data
        representation['proyecto'] = SimpleProjectSerializer(instance.proyecto).data
        representation['proveedor'] = ProveedorSerializer(instance.proveedor).data
        return representation

class OrdenDeCompraSerializer(serializers.ModelSerializer):
    # Campos para la lectura (GET)
    usuario_detail = SimpleUsuariosSerializer(source='usuario', read_only=True)
    proveedor_detail = ProveedorSerializer(source='proveedor', read_only=True)
    requisicion_detail = RequisicionSerializer(source='requisicion', read_only=True)

    # Campos para la escritura (POST)
    usuario = serializers.PrimaryKeyRelatedField(queryset=Usuarios.objects.all())
    proveedor = serializers.PrimaryKeyRelatedField(queryset=Proveedor.objects.all())
    requisicion = serializers.PrimaryKeyRelatedField(queryset=Requisicion.objects.all())

    class Meta:
        model = OrdenDeCompra
        fields = ['id', 'fecha_emision', 'fecha_entrega', 'proveedor', 'proveedor_detail', 'total', 'requisicion', 'requisicion_detail', 'usuario', 'usuario_detail','estado', 'url_pdf']

class ReciboSerializer(serializers.ModelSerializer):
    orden = OrdenDeCompraSerializer(many=True)

    class Meta:
        model = Recibo
        fields = ['orden', 'estado', 'descripcion']
