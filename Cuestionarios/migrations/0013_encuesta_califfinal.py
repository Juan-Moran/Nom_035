# Generated by Django 5.0.7 on 2024-09-06 01:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Cuestionarios', '0012_remove_categoria_muyalto_remove_cuestionario_muyalto_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='encuesta',
            name='califFinal',
            field=models.IntegerField(default=0),
        ),
    ]