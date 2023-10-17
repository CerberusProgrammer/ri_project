from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth.hashers import make_password
from simple_history.models import HistoricalRecords

class Producto(models.Model):
    MONEDAS = (
        ('MXN', 'MXN'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
    )
    
    identificador = models.CharField(max_length=100, null=True, help_text="Codigo o numero identificador")
    nombre = models.CharField(max_length=100, help_text="Nombre comercial del producto")
    descripcion = models.TextField(default="Sin descripcion")
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    divisa = models.CharField(max_length=5, default="MXN", choices=MONEDAS)
    cantidad = models.IntegerField(default=1)
    history = HistoricalRecords()

    def __str__(self):
        return self.nombre

class ProductoRequisicion(models.Model):
    MONEDAS = (
        ('MXN', 'MXN'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
    )
    
    identificador = models.CharField(max_length=100, null=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(default="Sin descripcion")
    cantidad = models.IntegerField(default=1)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    divisa = models.CharField(max_length=5, default="MXN", choices=MONEDAS)

    def __str__(self):
        return self.nombre

class Servicio(models.Model):
    MONEDAS = (
        ('MXN', 'MXN'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
    )
    
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    divisa = models.CharField(max_length=5, default="MXN", choices=MONEDAS)
    history = HistoricalRecords()

    def __str__(self):
        return self.nombre

class ServicioRequisicion(models.Model):
    MONEDAS = (
        ('MXN', 'MXN'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
    )
    
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    divisa = models.CharField(max_length=5, default="MXN", choices=MONEDAS)

    def __str__(self):
        return self.nombre

class Departamento(models.Model):
    MONEDAS = (
        ('MXN', 'MXN'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
    )
    
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(max_length=400, blank=True)
    presupuesto = models.DecimalField(max_digits=10, decimal_places=2, help_text="Dinero actual en el departamento.")
    ingreso_fijo = models.DecimalField(max_digits=10, decimal_places=2, help_text="El ingreso que se mantendra mes con mes.")
    divisa = models.CharField(max_length=5, default="MXN", choices=MONEDAS)
    history = HistoricalRecords()
    
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
        ('LIDER', 'Lider'),
        ('CALIDAD', 'Calidad'),
        ('DISEÑADOR', 'Diseñador'),
        ('OPERADOR', 'Operador'),
        ('PENDIENTE', 'Pendiente'),
    )

    is_staff = models.BooleanField(default=False)
    joined_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    username = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, blank=True)
    correo = models.EmailField(unique=True)
    rol = models.CharField(max_length=15, choices=PUESTOS, null=True)
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
    
    history = HistoricalRecords(inherit=True)

    @property
    def history_user(self):
        return self.username

    @history_user.setter
    def history_user(self, value):
        self._history_user = value

class Project(models.Model):
    MONEDAS = (
        ('MXN', 'MXN'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
    )
    
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(max_length=400, blank=True)
    presupuesto = models.DecimalField(max_digits=10, decimal_places=2, help_text="Dinero actual del proyecto.")
    divisa = models.CharField(max_length=5, default="MXN", choices=MONEDAS)
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name='proyectos')
    history = HistoricalRecords()

    def __str__(self):
        return self.nombre

class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    correo = models.EmailField(blank=True)
    history = HistoricalRecords()
    
    def __str__(self):
        return self.nombre

class Proveedor(models.Model):
    REGIMEN_FISCAL = (
        ('General de Ley Personas Morales', 'General de Ley Personas Morales'),
        ('Arrendamiento', 'Arrendamiento'),
        ('Personas Físicas con Actividades Empresariales y Profesionales', 'Personas Físicas con Actividades Empresariales y Profesionales'),
        ('Sin obligaciones fiscales', 'Sin obligaciones fiscales'),
        ('Incorporación Fiscal', 'Incorporación Fiscal'),
        ('Régimen Simplificado de Confianza', 'Régimen Simplificado de Confianza'),
    )

    nombre = models.CharField(max_length=100)
    razon_social = models.CharField(max_length=200)
    rfc = models.CharField(max_length=100)
    regimen_fiscal = models.CharField(max_length=150, choices=REGIMEN_FISCAL)
    codigo_postal = models.CharField(max_length=10)
    direccion = models.CharField(max_length=250, help_text="Ej. Avenida Soles #8193")
    direccion_geografica = models.CharField(max_length=100, help_text="Ej. Mexicali, B.C, Mexico")
    telefono = models.CharField(max_length=15, null=True)
    correo = models.EmailField(null=True)
    pagina = models.URLField(null=True)
    tiempo_de_entegra_estimado = models.CharField(max_length=120, null=True)
    iva = models.DecimalField(max_digits=10, decimal_places=10)
    iva_retenido = models.DecimalField(max_digits=10, decimal_places=10, null=True)
    isr_retenido = models.DecimalField(max_digits=10, decimal_places=10, null=True)
    dias_de_credito = models.CharField(max_length=100, null=True)
    credito = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    divisa = models.CharField(max_length=5, default='MXN')
    contactos = models.ManyToManyField(Contacto)
    calidad = models.DecimalField(max_digits=2, decimal_places=2, blank=True, help_text="0.0 al 0.9")
    history = HistoricalRecords()

    def __str__(self):
        return self.razon_social

class Requisicion(models.Model):
    ESTADO_APROBACION = (
        ('RECHAZADO', 'Rechazado'),
        ('PENDIENTE', 'Pendiente'),
        ('APROBADO', 'Aprobado'),
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    motivo = models.TextField(blank=True)
    total = models.IntegerField(default=0)
    aprobado = models.CharField(max_length=50, choices=ESTADO_APROBACION, default="PENDIENTE")
    ordenado = models.BooleanField(default=False)
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name='requisiciones', null=True)
    proyecto = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='requisiciones', null=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='requisiciones', null=True)
    productos = models.ManyToManyField(ProductoRequisicion, blank=True)
    servicios = models.ManyToManyField(ServicioRequisicion, blank=True)
    archivo_pdf = models.FileField(upload_to='pdfs/', blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return f'Requisicion de {self.usuario} | {self.fecha_creacion.day}/{self.fecha_creacion.month}/{self.fecha_creacion.year} {self.fecha_creacion.hour}:{self.fecha_creacion.minute}' # type: ignore

class OrdenDeCompra(models.Model):
    fecha_emision = models.DateTimeField(auto_now_add=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    requisicion = models.ForeignKey(Requisicion, on_delete=models.CASCADE, null=True)
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name='ordenes_de_compra', null=True)
    recibido = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return f'Orden de compra #{self.id}' # type: ignore

class Recibo(models.Model):
    orden = models.ManyToManyField(OrdenDeCompra, blank=False)
    estado = models.BooleanField(default=False)
    descripcion = models.CharField(max_length=255, default="Sin descripcion")
    history = HistoricalRecords()

    def __str__(self):
        return f'Recibo #{self.id}' # type: ignore

class Message(models.Model):
    user = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name='messages')
    from_user = models.ForeignKey(Usuarios, on_delete=models.DO_NOTHING, related_query_name=None)
    title = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.from_user} to {self.user} | {self.created_at.day}/{self.created_at.month}/{self.created_at.year} {self.created_at.hour}:{self.created_at.minute}' # type: ignore