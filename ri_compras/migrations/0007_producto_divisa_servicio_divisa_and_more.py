# Generated by Django 4.2.5 on 2023-09-29 23:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ri_compras', '0006_producto_identificador_alter_producto_cantidad_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='divisa',
            field=models.CharField(default='MXN', max_length=5),
        ),
        migrations.AddField(
            model_name='servicio',
            name='divisa',
            field=models.CharField(default='MXN', max_length=5),
        ),
        migrations.AlterField(
            model_name='usuarios',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$600000$QwmPkEn9033QYWE9WGqZVJ$wR36wKdtVw7tJYlJI7WxvKBxd4ageuxSxT5UuneCEow=', max_length=128),
        ),
    ]
