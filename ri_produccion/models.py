from django.db import models
from ri_compras.models import Usuarios

class Material(models.Model):
    nombre = models.CharField(max_length=100)
    necesitaNesteo = models.BooleanField(default=True)
    espesor = models.CharField(max_length=100)
    proveedor = models.CharField(max_length=120)

    def __str__(self):
        return self.nombre

class Placa(models.Model):
    piezas = models.IntegerField()

    def __str__(self):
        return str(self.piezas)

class Proceso(models.Model):
    nombre = models.CharField(max_length=100)
    estatus = models.CharField(max_length=50)
    maquina = models.CharField(max_length=100)
    inicioProceso = models.DateTimeField()
    finProceso = models.DateTimeField()
    placa = models.ForeignKey(Placa, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

class Pieza(models.Model):
    consecutivo = models.CharField(max_length=100, unique=True)
    ordenCompra = models.CharField(max_length=150)
    piezas = models.IntegerField()
    piezasTotales = models.IntegerField()
    material = models.ForeignKey(Material, on_delete=models.CASCADE, null=True, blank=True)
    placas = models.ManyToManyField(Placa, blank=True)
    procesos = models.ManyToManyField(Proceso, blank=True)
    creadoPor = models.ForeignKey(Usuarios, on_delete=models.CASCADE, null=True, blank=True)
    archivo_pdf = models.FileField(upload_to='pdfs-produccion', blank=True, null=True)

    def __str__(self):
        return self.consecutivo
