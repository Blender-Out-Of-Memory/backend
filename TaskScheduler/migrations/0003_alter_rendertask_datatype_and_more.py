# Generated by Django 4.0.6 on 2024-06-24 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TaskScheduler', '0002_rendertaskmodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rendertask',
            name='dataType',
            field=models.CharField(max_length=1),
        ),
        migrations.AlterField(
            model_name='rendertask',
            name='outputType',
            field=models.CharField(max_length=1),
        ),
    ]
