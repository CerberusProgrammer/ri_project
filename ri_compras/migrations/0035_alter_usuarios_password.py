# Generated by Django 4.2.5 on 2023-09-13 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ri_compras', '0034_alter_usuarios_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuarios',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$600000$z9UArsHayxKvhy8R2KDVU6$WQgCgfDVvrMfrTLDisc9QvzfIgnoj1il2YoSYC9p3oY=', max_length=128),
        ),
    ]
