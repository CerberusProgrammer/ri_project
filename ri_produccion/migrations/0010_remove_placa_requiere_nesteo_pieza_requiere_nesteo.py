# Generated by Django 4.2.5 on 2023-12-05 22:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ri_produccion', '0009_alter_placa_requiere_nesteo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='placa',
            name='requiere_nesteo',
        ),
        migrations.AddField(
            model_name='pieza',
            name='requiere_nesteo',
            field=models.BooleanField(default=True),
        ),
    ]