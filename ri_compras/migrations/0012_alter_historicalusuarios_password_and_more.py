# Generated by Django 4.2.5 on 2023-11-11 00:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ri_compras', '0011_alter_historicalusuarios_password_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalusuarios',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$600000$E0svSZwhKh3DxWpD1mcot2$Pq2BztpFQhH8xF4FScv3MW/IakdAe24Cnfurl0LtRYs=', max_length=128),
        ),
        migrations.AlterField(
            model_name='usuarios',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$600000$E0svSZwhKh3DxWpD1mcot2$Pq2BztpFQhH8xF4FScv3MW/IakdAe24Cnfurl0LtRYs=', max_length=128),
        ),
    ]
