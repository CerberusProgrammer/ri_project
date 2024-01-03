from django.db import models
from django.utils import timezone
from ri_compras.models import Usuarios

class Material(models.Model):
    nombre = models.CharField(max_length=100)
    espesor = models.CharField(max_length=100)
    proveedor = models.CharField(max_length=120)

    def __str__(self):
        return self.nombre

class Placa(models.Model):
    nombre = models.CharField(max_length=100, null=True, blank=True)
    descripcion = models.CharField(max_length=350, null=True, blank=True)
    piezas = models.IntegerField(null=True, blank=True)
    
    def num_procesos(self):
        return self.proceso_set.count()
    
    def todos_procesos_ligados(self):
        return all(proceso.placa is not None for proceso in self.proceso_set.all())

    def __str__(self):
        return str(self.nombre)

class Proceso(models.Model):
    ESTATUS_CHOICES = [
        ('error', 'Error'),
        ('rechazado', 'Rechañado'),
        ('pendiente', 'Pendiente'),
        ('operando', 'Operando'),
        ('realizado', 'Realizado'),
    ]

    nombre = models.CharField(max_length=100)
    piezasRealizadas = models.IntegerField(null=True, blank=True)
    estatus = models.CharField(max_length=50, choices=ESTATUS_CHOICES, default="pendiente")
    maquina = models.CharField(max_length=100)
    inicioProceso = models.DateTimeField()
    finProceso = models.DateTimeField()
    terminadoProceso = models.DateTimeField(null=True, blank=True)
    placa = models.ForeignKey(Placa, on_delete=models.CASCADE,null=True, blank=True)
    realizadoPor = models.ForeignKey(Usuarios, on_delete=models.CASCADE, null=True, blank=True)
    comentarios = models.CharField(max_length=300, null=True, blank=True)
    prioridad = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre

class Pieza(models.Model):
    STATUS_CHOICES = [
        ('rechazado', 'Rechazado'),
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('revision', 'Revision'),
    ]
    
    CALIDAD_CHOICES = [
        ('dimensional', 'Dimensional'),
        ('pintura', 'Pintura'),
        ('proveedor', 'Proveedor'),
        ('ninguno', 'Ninguno'),
    ]
    
    piezas = models.IntegerField()
    piezasRechazadas = models.IntegerField(default=0)
    piezasTotales = models.IntegerField()
    piezaRealizada = models.BooleanField(default=False)
    tipo_calidad = models.CharField(max_length=40, choices=CALIDAD_CHOICES, default="dimensional")
    tipo_tratamientos = models.CharField(max_length=200, blank=True, null=True)
    proveedor_entrega_estimada = models.DateTimeField(null=True, blank=True)
    proveedor_entrega_enviado = models.DateTimeField(null=True, blank=True)
    requiere_nesteo = models.BooleanField(default=True)
    consecutivo = models.CharField(max_length=100, unique=True)
    estatus = models.CharField(max_length=40, choices=STATUS_CHOICES, default="pendiente")
    estatusAsignacion = models.BooleanField(default=False)
    motivoRechazo = models.CharField(max_length=300, blank=True, null=True)
    fechaRechazado = models.DateTimeField(null=True)
    ordenCompra = models.CharField(max_length=150)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, null=True, blank=True)
    placas = models.ManyToManyField(Placa, through='PiezaPlaca', blank=True)
    nombreProceso = models.CharField(max_length=100, blank=True, null=True)
    procesos = models.ManyToManyField(Proceso, blank=True)
    creadoPor = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    fechaCreado = models.DateTimeField(auto_now_add=True)
    archivo_pdf = models.FileField(upload_to='pdfs-produccion', blank=True, null=True)
    prioridad = models.BooleanField(default=False)

    def esta_retrasada(self):
        return any(proceso.finProceso < timezone.now() and proceso.estatus != 'realizado' for proceso in self.procesos.all())

    def __str__(self):
        return self.consecutivo

class PiezaPlaca(models.Model):
    pieza = models.ForeignKey(Pieza, on_delete=models.CASCADE)
    placa = models.ForeignKey(Placa, on_delete=models.CASCADE)
    piezas_realizadas = models.IntegerField(default=0)

class Notificacion(models.Model):
    titulo = models.CharField(max_length=100)
    contenido = models.TextField()
    leido = models.BooleanField(default=False)
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo