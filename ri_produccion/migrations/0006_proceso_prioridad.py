# Generated by Django 4.2.5 on 2023-11-13 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ri_produccion', '0005_proceso_comentarios_proceso_realizadopor_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='proceso',
            name='prioridad',
            field=models.BooleanField(default=False),
        ),
    ]
