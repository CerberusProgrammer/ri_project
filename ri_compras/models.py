from django.db import models
from django.utils import timezone

class Usuarios(models.Model):
    PUESTOS = (
        ('MASTER', 'Master'),
        ('ADMINISTRADOR', 'Administrador'),
        ('SUPERVISOR', 'Supervisor'),
        ('COMPRADOR', 'Comprador'),
        ('CALIDAD', 'Calidad'),
        ('DISEÑADOR', 'Diseñador'),
        ('OPERADOR', 'Operador'),
    )
    token = models.CharField(max_length=50)
    joined_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    username = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    correo = models.EmailField(unique=True)
    rol = models.CharField(max_length=15, choices=PUESTOS)
