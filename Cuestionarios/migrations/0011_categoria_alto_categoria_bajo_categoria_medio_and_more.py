# Generated by Django 5.0.7 on 2024-09-04 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Cuestionarios', '0010_alter_control_secuencia'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoria',
            name='alto',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='categoria',
            name='bajo',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='categoria',
            name='medio',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='categoria',
            name='muyAlto',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='categoria',
            name='nulo',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cuestionario',
            name='alto',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cuestionario',
            name='bajo',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cuestionario',
            name='medio',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cuestionario',
            name='muyAlto',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cuestionario',
            name='nulo',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dominio',
            name='alto',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dominio',
            name='bajo',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dominio',
            name='medio',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dominio',
            name='muyAlto',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dominio',
            name='nulo',
            field=models.SmallIntegerField(default=0),
        ),
    ]
