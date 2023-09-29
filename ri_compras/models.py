from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth.hashers import make_password

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    cantidad = models.IntegerField()
    costo = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre

class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    costo = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre

class Departamento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(max_length=400, blank=True)
    presupuesto = models.DecimalField(max_digits=10, decimal_places=2)
    limite = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    def __str__(self):
        return self.nombre

class UsuariosManager(BaseUserManager):
    def create_user(self, username, correo=None, password=None):
        if not username:
            raise ValueError('El nombre de usuario es obligatorio')
        if not correo:
            raise ValueError('El correo electrónico es obligatorio')

        user = self.model(username=username, correo=correo)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, correo, password=None):
        if not password:
            raise ValueError('La contraseña es obligatoria')

        user = self.create_user(username, correo, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, username):
        return self.get(username=username)

class Usuarios(AbstractBaseUser, PermissionsMixin):
    PUESTOS = (
        ('MASTER', 'Master'),
        ('ADMINISTRADOR', 'Administrador'),
        ('SUPERVISOR', 'Supervisor'),
        ('COMPRADOR', 'Comprador'),
        ('CALIDAD', 'Calidad'),
        ('DISEÑADOR', 'Diseñador'),
        ('OPERADOR', 'Operador'),
    )

    joined_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    username = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    correo = models.EmailField(unique=True)
    rol = models.CharField(max_length=15, choices=PUESTOS)
    is_staff = models.BooleanField(default=False)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='usuarios', null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['correo']

    password = models.CharField(max_length=128, default=make_password('default'))

    objects = UsuariosManager()

    groups = models.ManyToManyField(
        Group,
        verbose_name=('groups'),
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="ri_compras_usuarios_set",
        related_query_name="user",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=('user permissions'),
        blank=True,
        help_text=('Specific permissions for this user.'),
        related_name="ri_compras_usuarios_set",
        related_query_name="user",
    )

class Project(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(max_length=400, blank=True)
    presupuesto = models.DecimalField(max_digits=10, decimal_places=2)
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name='proyectos', null=True)

class Requisicion(models.Model):
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    productos = models.ManyToManyField(Producto, blank=True)
    servicios = models.ManyToManyField(Servicio, blank=True)
    motivo = models.TextField(blank=True)
    aprobado = models.BooleanField(default=False)
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name='requisiciones', null=True)

    def __str__(self):
        return self.motivo

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=15, blank=True)
    correo = models.EmailField(blank=True)
    pagina = models.URLField(blank=True)
    calidad = models.DecimalField(max_digits=2, decimal_places=2, null=True)
    tiempo_de_entegra_estimado = models.DateTimeField(null=True)

    def __str__(self):
        return self.nombre

class OrdenDeCompra(models.Model):
    fecha_emision = models.DateTimeField(auto_now_add=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0) # type: ignore
    requisiciones = models.ManyToManyField(Requisicion)
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name='ordenes_de_compra', null=True)

    def __str__(self):
        return f'Orden de compra #{self.id}' # type: ignore

class Recibo(models.Model):
    orden = models.ManyToManyField(OrdenDeCompra, blank=False)
    estado = models.BooleanField(default=False)
    descripcion = models.CharField(max_length=255, default="Sin descripcion")

    def __str__(self):
        return f'Recibo #{self.id}' # type: ignore