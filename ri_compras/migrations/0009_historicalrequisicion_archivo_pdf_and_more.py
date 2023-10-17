# Generated by Django 4.2.5 on 2023-10-14 04:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ri_compras', '0008_alter_historicalusuarios_password_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalrequisicion',
            name='archivo_pdf',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='requisicion',
            name='archivo_pdf',
            field=models.FileField(blank=True, null=True, upload_to='pdfs/'),
        ),
        migrations.AlterField(
            model_name='historicalusuarios',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$600000$Pftc3dqXSTEbLgzqqg32dO$5LAjYOgISUK3rOZuDPTEzLhA/HT2d6Vq5SmInDHbg60=', max_length=128),
        ),
        migrations.AlterField(
            model_name='usuarios',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$600000$Pftc3dqXSTEbLgzqqg32dO$5LAjYOgISUK3rOZuDPTEzLhA/HT2d6Vq5SmInDHbg60=', max_length=128),
        ),
    ]