# Generated by Django 5.0.7 on 2024-08-29 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Cuestionarios', '0007_alter_trabajador_nombre'),
    ]

    operations = [
        migrations.AddField(
            model_name='encuesta',
            name='seccion',
            field=models.SmallIntegerField(default=0),
        ),
    ]
