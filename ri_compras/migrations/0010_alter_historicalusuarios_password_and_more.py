# Generated by Django 4.2.5 on 2023-10-16 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ri_compras', '0009_historicalrequisicion_archivo_pdf_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalusuarios',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$600000$kweLgBbcaPl09umIZTd0Zh$0Mu5lYuNMjZIAW5t+iiWG0hrTnSV8hGzuRwUEvH4hkA=', max_length=128),
        ),
        migrations.AlterField(
            model_name='usuarios',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$600000$kweLgBbcaPl09umIZTd0Zh$0Mu5lYuNMjZIAW5t+iiWG0hrTnSV8hGzuRwUEvH4hkA=', max_length=128),
        ),
    ]
