# Generated by Django 4.2.5 on 2023-09-13 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ri_compras', '0035_alter_usuarios_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuarios',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$600000$zKDOPmT0cYVnxeD0s8SgI8$AZfqMqeafl0BGVHDbvt86ycXfAHPB8BZkSWcoI4G+Gw=', max_length=128),
        ),
    ]
