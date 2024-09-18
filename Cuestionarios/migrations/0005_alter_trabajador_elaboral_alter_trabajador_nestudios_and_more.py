# Generated by Django 5.0.7 on 2024-08-13 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Cuestionarios', '0004_empresa_numero'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trabajador',
            name='eLaboral',
            field=models.CharField(choices=[('1', 'Menos de 6 meses'), ('2', 'Entre 6 meses y 1 año'), ('3', 'Entre 1 a 4 años'), ('4', 'Entre 5 a 9 años'), ('5', 'Entre 10 a 14 años'), ('6', 'Entre 15 a 19 años'), ('7', 'Entre 20 a 24 años'), ('8', '25 años o más')], default='3', max_length=1, verbose_name='Experiencia laboral'),
        ),
        migrations.AlterField(
            model_name='trabajador',
            name='nEstudios',
            field=models.CharField(choices=[('1', 'Primaria'), ('2', 'Secundaria'), ('3', 'Bachillerato o Preparatoria'), ('4', 'Técnico Superior'), ('5', 'Licenciatura'), ('6', 'Maestría'), ('7', 'Doctorado')], default='1', max_length=1, verbose_name='Nivel de estudios'),
        ),
        migrations.AlterField(
            model_name='trabajador',
            name='tContrato',
            field=models.CharField(choices=[('O', 'Por Obra o proyecto'), ('I', 'Tiempo indeterminado'), ('T', 'Tiempo determinado o Temporal'), ('H', 'Honorarios')], default='I', max_length=1, verbose_name='Tipo de contrato'),
        ),
        migrations.AlterField(
            model_name='trabajador',
            name='tJornada',
            field=models.CharField(choices=[('D', 'Fijo diurno (entre las 6:00 y 20:00 hrs)'), ('N', 'Fijo nocturno (entre las 20:00 y 6:00 hrs)'), ('M', 'Fijo mixto (combinación de nocturno y diurno)')], default='D', max_length=1, verbose_name='Tipo de jornada'),
        ),
        migrations.AlterField(
            model_name='trabajador',
            name='tPersonal',
            field=models.CharField(choices=[('S', 'Sindicalizado'), ('C', 'Confianza'), ('N', 'Ninguno')], default='N', max_length=1, verbose_name='Tipo de personal'),
        ),
        migrations.AlterField(
            model_name='trabajador',
            name='tPuesto',
            field=models.CharField(choices=[('O', 'Operativo'), ('S', 'Supervisor'), ('P', 'Profesional o técnico'), ('G', 'Gerente')], default='o', max_length=1, verbose_name='Tipo de puesto'),
        ),
    ]