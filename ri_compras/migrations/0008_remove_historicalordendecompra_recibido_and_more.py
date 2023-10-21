# Generated by Django 4.2.5 on 2023-10-21 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ri_compras', '0007_historicalrequisicion_fecha_aprobado_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalordendecompra',
            name='recibido',
        ),
        migrations.RemoveField(
            model_name='ordendecompra',
            name='recibido',
        ),
        migrations.AddField(
            model_name='historicalordendecompra',
            name='estado',
            field=models.CharField(choices=[('RECHAZADO', 'RECHAZADO'), ('EN SOLICITUD', 'EN SOLICITUD'), ('EN CAMINO', 'EN CAMINO'), ('EN ALMACEN', 'EN ALMACEN')], default='EN SOLICITUD', max_length=50),
        ),
        migrations.AddField(
            model_name='historicalordendecompra',
            name='fecha_entrega',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='historicalrequisicion',
            name='fecha_entrega_estimada',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='ordendecompra',
            name='estado',
            field=models.CharField(choices=[('RECHAZADO', 'RECHAZADO'), ('EN SOLICITUD', 'EN SOLICITUD'), ('EN CAMINO', 'EN CAMINO'), ('EN ALMACEN', 'EN ALMACEN')], default='EN SOLICITUD', max_length=50),
        ),
        migrations.AddField(
            model_name='ordendecompra',
            name='fecha_entrega',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='requisicion',
            name='fecha_entrega_estimada',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='historicalusuarios',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$600000$pU1Yu14xpc0nQqV6MMicHl$PKCycKD+tD9n/T4dJj63otkbCzaB7X1OZbZuN7H+RTQ=', max_length=128),
        ),
        migrations.AlterField(
            model_name='usuarios',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$600000$pU1Yu14xpc0nQqV6MMicHl$PKCycKD+tD9n/T4dJj63otkbCzaB7X1OZbZuN7H+RTQ=', max_length=128),
        ),
    ]
