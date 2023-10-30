# Generated by Django 4.2.5 on 2023-10-27 23:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ri_compras', '0003_alter_usuarios_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proveedor',
            name='credito',
            field=models.DecimalField(decimal_places=8, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='usuarios',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$600000$4yonONVGjfESdOP3CZ8sac$hLAju8e4kd5GBrmbdOwanlLTCko2w/Lr8grZ0UuXgh0=', max_length=128),
        ),
    ]
