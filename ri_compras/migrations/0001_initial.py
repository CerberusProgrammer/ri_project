# Generated by Django 4.2.5 on 2023-10-05 22:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuarios',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False)),
                ('joined_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
                ('username', models.CharField(max_length=50, unique=True)),
                ('nombre', models.CharField(max_length=100)),
                ('telefono', models.CharField(max_length=15, null=True)),
                ('correo', models.EmailField(max_length=254, unique=True)),
                ('rol', models.CharField(choices=[('MASTER', 'Master'), ('ADMINISTRADOR', 'Administrador'), ('SUPERVISOR', 'Supervisor'), ('COMPRADOR', 'Comprador'), ('LIDER', 'Lider'), ('CALIDAD', 'Calidad'), ('DISEÑADOR', 'Diseñador'), ('OPERADOR', 'Operador'), ('PENDIENTE', 'Pendiente')], max_length=15, null=True)),
                ('password', models.CharField(default='pbkdf2_sha256$600000$EZvyYAYPPZzxzINNtE04ZM$bjZ/iUrNhfl1qP8AvoKqPJs8k5cnGI+Tc/+QlL7qDgs=', max_length=128)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Contacto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('direccion', models.CharField(max_length=100)),
                ('telefono', models.CharField(max_length=15)),
                ('correo', models.EmailField(blank=True, max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Departamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('descripcion', models.TextField(blank=True, max_length=400)),
                ('presupuesto', models.DecimalField(decimal_places=2, help_text='Dinero actual en el departamento.', max_digits=10)),
                ('ingreso_fijo', models.DecimalField(decimal_places=2, help_text='El ingreso que se mantendra mes con mes.', max_digits=10)),
                ('divisa', models.CharField(choices=[('MXN', 'MXN'), ('USD', 'USD'), ('EUR', 'EUR')], default='MXN', max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='OrdenDeCompra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_emision', models.DateTimeField(auto_now_add=True)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('recibido', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identificador', models.CharField(help_text='Codigo o numero identificador', max_length=100, null=True)),
                ('nombre', models.CharField(help_text='Nombre comercial del producto', max_length=100)),
                ('descripcion', models.TextField(default='Sin descripcion')),
                ('costo', models.DecimalField(decimal_places=2, max_digits=10)),
                ('divisa', models.CharField(choices=[('MXN', 'MXN'), ('USD', 'USD'), ('EUR', 'EUR')], default='MXN', max_length=5)),
                ('cantidad', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='ProductoRequisicion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identificador', models.CharField(max_length=100, null=True)),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField(default='Sin descripcion')),
                ('cantidad', models.IntegerField(default=1)),
                ('costo', models.DecimalField(decimal_places=2, max_digits=10)),
                ('divisa', models.CharField(choices=[('MXN', 'MXN'), ('USD', 'USD'), ('EUR', 'EUR')], default='MXN', max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('descripcion', models.TextField(blank=True, help_text='Dinero actual del proyecto.', max_length=400)),
                ('presupuesto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('divisa', models.CharField(choices=[('MXN', 'MXN'), ('USD', 'USD'), ('EUR', 'EUR')], default='MXN', max_length=5)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proyectos', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Proveedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('razon_social', models.CharField(blank=True, max_length=200)),
                ('rfc', models.CharField(blank=True, max_length=100)),
                ('regimen_fiscal', models.CharField(choices=[('MASTER', 'Master')], max_length=50, null=True)),
                ('codigo_postal', models.CharField(max_length=10)),
                ('direccion', models.CharField(blank=True, help_text='Ej. Avenida Soles #8193', max_length=100)),
                ('direccion_geografica', models.CharField(blank=True, help_text='Ej. Mexicali, B.C, Mexico', max_length=100)),
                ('telefono', models.CharField(blank=True, max_length=15)),
                ('correo', models.EmailField(blank=True, max_length=254)),
                ('pagina', models.URLField(blank=True)),
                ('tiempo_de_entegra_estimado', models.CharField(blank=True, max_length=120)),
                ('iva', models.DecimalField(decimal_places=2, max_digits=2)),
                ('isr', models.DecimalField(decimal_places=2, max_digits=2)),
                ('dias_de_credito', models.CharField(blank=True, max_length=100)),
                ('credito', models.DecimalField(blank=True, decimal_places=2, max_digits=10)),
                ('divisa', models.CharField(default='MXN', max_length=5)),
                ('grupo', models.CharField(blank=True, help_text='Ej. Metales', max_length=100)),
                ('categoria', models.CharField(blank=True, help_text='Tornillo de Acero', max_length=100)),
                ('calidad', models.DecimalField(blank=True, decimal_places=2, help_text='1 al 10', max_digits=2)),
            ],
        ),
        migrations.CreateModel(
            name='Servicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
                ('costo', models.DecimalField(decimal_places=2, max_digits=10)),
                ('divisa', models.CharField(choices=[('MXN', 'MXN'), ('USD', 'USD'), ('EUR', 'EUR')], default='MXN', max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='ServicioRequisicion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
                ('costo', models.DecimalField(decimal_places=2, max_digits=10)),
                ('divisa', models.CharField(choices=[('MXN', 'MXN'), ('USD', 'USD'), ('EUR', 'EUR')], default='MXN', max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='Requisicion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('motivo', models.TextField(blank=True)),
                ('total', models.IntegerField(default=0)),
                ('aprobado', models.BooleanField(default=False)),
                ('ordenado', models.BooleanField(default=False)),
                ('productos', models.ManyToManyField(blank=True, to='ri_compras.productorequisicion')),
                ('proveedor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='requisiciones', to='ri_compras.proveedor')),
                ('proyecto', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='requisiciones', to='ri_compras.project')),
                ('servicios', models.ManyToManyField(blank=True, to='ri_compras.serviciorequisicion')),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='requisiciones', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Recibo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.BooleanField(default=False)),
                ('descripcion', models.CharField(default='Sin descripcion', max_length=255)),
                ('orden', models.ManyToManyField(to='ri_compras.ordendecompra')),
            ],
        ),
        migrations.AddField(
            model_name='ordendecompra',
            name='proveedor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ri_compras.proveedor'),
        ),
        migrations.AddField(
            model_name='ordendecompra',
            name='requisicion',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ri_compras.requisicion'),
        ),
        migrations.AddField(
            model_name='ordendecompra',
            name='usuario',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ordenes_de_compra', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='HistoricalUsuarios',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False)),
                ('joined_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
                ('username', models.CharField(db_index=True, max_length=50)),
                ('nombre', models.CharField(max_length=100)),
                ('telefono', models.CharField(max_length=15, null=True)),
                ('correo', models.EmailField(db_index=True, max_length=254)),
                ('rol', models.CharField(choices=[('MASTER', 'Master'), ('ADMINISTRADOR', 'Administrador'), ('SUPERVISOR', 'Supervisor'), ('COMPRADOR', 'Comprador'), ('LIDER', 'Lider'), ('CALIDAD', 'Calidad'), ('DISEÑADOR', 'Diseñador'), ('OPERADOR', 'Operador'), ('PENDIENTE', 'Pendiente')], max_length=15, null=True)),
                ('password', models.CharField(default='pbkdf2_sha256$600000$EZvyYAYPPZzxzINNtE04ZM$bjZ/iUrNhfl1qP8AvoKqPJs8k5cnGI+Tc/+QlL7qDgs=', max_length=128)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('departamento', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ri_compras.departamento')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical usuarios',
                'verbose_name_plural': 'historical usuarioss',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalServicio',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
                ('costo', models.DecimalField(decimal_places=2, max_digits=10)),
                ('divisa', models.CharField(choices=[('MXN', 'MXN'), ('USD', 'USD'), ('EUR', 'EUR')], default='MXN', max_length=5)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical servicio',
                'verbose_name_plural': 'historical servicios',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalRequisicion',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(blank=True, editable=False)),
                ('motivo', models.TextField(blank=True)),
                ('total', models.IntegerField(default=0)),
                ('aprobado', models.BooleanField(default=False)),
                ('ordenado', models.BooleanField(default=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('proveedor', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ri_compras.proveedor')),
                ('proyecto', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ri_compras.project')),
                ('usuario', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical requisicion',
                'verbose_name_plural': 'historical requisicions',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalRecibo',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('estado', models.BooleanField(default=False)),
                ('descripcion', models.CharField(default='Sin descripcion', max_length=255)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical recibo',
                'verbose_name_plural': 'historical recibos',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalProveedor',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('razon_social', models.CharField(blank=True, max_length=200)),
                ('rfc', models.CharField(blank=True, max_length=100)),
                ('regimen_fiscal', models.CharField(choices=[('MASTER', 'Master')], max_length=50, null=True)),
                ('codigo_postal', models.CharField(max_length=10)),
                ('direccion', models.CharField(blank=True, help_text='Ej. Avenida Soles #8193', max_length=100)),
                ('direccion_geografica', models.CharField(blank=True, help_text='Ej. Mexicali, B.C, Mexico', max_length=100)),
                ('telefono', models.CharField(blank=True, max_length=15)),
                ('correo', models.EmailField(blank=True, max_length=254)),
                ('pagina', models.URLField(blank=True)),
                ('tiempo_de_entegra_estimado', models.CharField(blank=True, max_length=120)),
                ('iva', models.DecimalField(decimal_places=2, max_digits=2)),
                ('isr', models.DecimalField(decimal_places=2, max_digits=2)),
                ('dias_de_credito', models.CharField(blank=True, max_length=100)),
                ('credito', models.DecimalField(blank=True, decimal_places=2, max_digits=10)),
                ('divisa', models.CharField(default='MXN', max_length=5)),
                ('grupo', models.CharField(blank=True, help_text='Ej. Metales', max_length=100)),
                ('categoria', models.CharField(blank=True, help_text='Tornillo de Acero', max_length=100)),
                ('calidad', models.DecimalField(blank=True, decimal_places=2, help_text='1 al 10', max_digits=2)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical proveedor',
                'verbose_name_plural': 'historical proveedors',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalProject',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('nombre', models.CharField(db_index=True, max_length=100)),
                ('descripcion', models.TextField(blank=True, help_text='Dinero actual del proyecto.', max_length=400)),
                ('presupuesto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('divisa', models.CharField(choices=[('MXN', 'MXN'), ('USD', 'USD'), ('EUR', 'EUR')], default='MXN', max_length=5)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('usuario', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical project',
                'verbose_name_plural': 'historical projects',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalProducto',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('identificador', models.CharField(help_text='Codigo o numero identificador', max_length=100, null=True)),
                ('nombre', models.CharField(help_text='Nombre comercial del producto', max_length=100)),
                ('descripcion', models.TextField(default='Sin descripcion')),
                ('costo', models.DecimalField(decimal_places=2, max_digits=10)),
                ('divisa', models.CharField(choices=[('MXN', 'MXN'), ('USD', 'USD'), ('EUR', 'EUR')], default='MXN', max_length=5)),
                ('cantidad', models.IntegerField(default=1)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical producto',
                'verbose_name_plural': 'historical productos',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalOrdenDeCompra',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('fecha_emision', models.DateTimeField(blank=True, editable=False)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('recibido', models.BooleanField(default=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('proveedor', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ri_compras.proveedor')),
                ('requisicion', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='ri_compras.requisicion')),
                ('usuario', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical orden de compra',
                'verbose_name_plural': 'historical orden de compras',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalDepartamento',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('nombre', models.CharField(db_index=True, max_length=100)),
                ('descripcion', models.TextField(blank=True, max_length=400)),
                ('presupuesto', models.DecimalField(decimal_places=2, help_text='Dinero actual en el departamento.', max_digits=10)),
                ('ingreso_fijo', models.DecimalField(decimal_places=2, help_text='El ingreso que se mantendra mes con mes.', max_digits=10)),
                ('divisa', models.CharField(choices=[('MXN', 'MXN'), ('USD', 'USD'), ('EUR', 'EUR')], default='MXN', max_length=5)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical departamento',
                'verbose_name_plural': 'historical departamentos',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalContacto',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('direccion', models.CharField(max_length=100)),
                ('telefono', models.CharField(max_length=15)),
                ('correo', models.EmailField(blank=True, max_length=254)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical contacto',
                'verbose_name_plural': 'historical contactos',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.AddField(
            model_name='usuarios',
            name='departamento',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='usuarios', to='ri_compras.departamento'),
        ),
        migrations.AddField(
            model_name='usuarios',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='ri_compras_usuarios_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='usuarios',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='ri_compras_usuarios_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
    ]
