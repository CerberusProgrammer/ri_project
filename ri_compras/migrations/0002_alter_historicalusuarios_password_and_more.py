# Generated by Django 4.2.5 on 2023-10-05 22:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ri_compras', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalusuarios',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$600000$tZZ6rfyvxuiN4qwF46zZgb$h5BDIjsZ077aSaSWefNSXzBsxtTons5kkvTr6ztiFDU=', max_length=128),
        ),
        migrations.AlterField(
            model_name='usuarios',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$600000$tZZ6rfyvxuiN4qwF46zZgb$h5BDIjsZ077aSaSWefNSXzBsxtTons5kkvTr6ztiFDU=', max_length=128),
        ),
    ]