# Generated by Django 4.2.3 on 2023-08-10 15:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_probehardware_probe_hardware'),
    ]

    operations = [
        migrations.AlterField(
            model_name='probe',
            name='hardware',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.probehardware'),
        ),
    ]