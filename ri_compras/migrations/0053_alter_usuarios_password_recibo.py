# Generated by Django 4.2.5 on 2023-09-14 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ri_compras', '0052_alter_usuarios_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuarios',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$600000$BEo2kWdXSAKGCA4WhQgnzL$3ad0nrQIIiaeZpZtKDl6CNYJljBhNIQMVBOCtnFs9AI=', max_length=128),
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
    ]
