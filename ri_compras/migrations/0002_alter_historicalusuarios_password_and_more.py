# Generated by Django 4.2.5 on 2023-10-13 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ri_compras', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalusuarios',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$600000$eqaCO4rnYmLryqsNr1ebg0$mtUyZgq7w0c+OeqbOTKIP1/TW5ziIviH4wdAuzXSDO0=', max_length=128),
        ),
        migrations.AlterField(
            model_name='usuarios',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$600000$eqaCO4rnYmLryqsNr1ebg0$mtUyZgq7w0c+OeqbOTKIP1/TW5ziIviH4wdAuzXSDO0=', max_length=128),
        ),
    ]
