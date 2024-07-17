# Generated by Django 5.0.7 on 2024-07-17 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TaskScheduler', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rendertask',
            name='Stage',
            field=models.CharField(choices=[('1-PEN', 'Pending'), ('2-REN', 'Rendering'), ('3-CON', 'Concatenating'), ('4-FIN', 'Finished'), ('5-EXP', 'Expired')], max_length=5),
        ),
        migrations.AlterField(
            model_name='subtask',
            name='Stage',
            field=models.CharField(choices=[('1-PEN', 'Pending'), ('2-TRA', 'Transferring'), ('3-RUN', 'Running'), ('4-FIN', 'Finished'), ('5-ABO', 'Aborted')], default='1-PEN', max_length=5),
        ),
    ]
