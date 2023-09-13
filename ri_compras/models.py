from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission
from django.contrib.auth.hashers import make_password

class Departamento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    presupuesto = models.DecimalField(max_digits=10, decimal_places=2)

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
