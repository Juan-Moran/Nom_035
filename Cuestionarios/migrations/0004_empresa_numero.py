# Generated by Django 5.0.7 on 2024-08-12 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Cuestionarios', '0003_remove_empresario_contraseña_empresario_apellido_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='empresa',
            name='numero',
            field=models.SmallIntegerField(default=1),
        ),
    ]
