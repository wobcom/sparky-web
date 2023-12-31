# Generated by Django 4.2.3 on 2023-08-25 10:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_alter_probe_hardware'),
    ]

    operations = [
        migrations.AddField(
            model_name='probe',
            name='metrics_bearer',
            field=models.CharField(max_length=32, null=True, unique=True, validators=[django.core.validators.MinLengthValidator(32)], verbose_name='Metrics bearer token'),
        ),
    ]
