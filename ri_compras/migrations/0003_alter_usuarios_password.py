# Generated by Django 4.2.5 on 2023-10-27 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ri_compras', '0002_alter_usuarios_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuarios',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$600000$SMOhuNPh0UlPamMtoGoLgS$1dqh0VWYRX0rX93kZArhb4bxFQJBi/U+JhuxHwPq1oQ=', max_length=128),
        ),
    ]