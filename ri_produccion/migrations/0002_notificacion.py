# Generated by Django 4.2.5 on 2023-11-16 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ri_produccion', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mensaje', models.CharField(max_length=300)),
            ],
        ),
    ]