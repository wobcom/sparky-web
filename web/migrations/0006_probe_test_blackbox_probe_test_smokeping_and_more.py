# Generated by Django 4.2.3 on 2023-09-11 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_alter_probe_metrics_bearer'),
    ]

    operations = [
        migrations.AddField(
            model_name='probe',
            name='test_blackbox',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='probe',
            name='test_smokeping',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='probe',
            name='test_traceroute',
            field=models.BooleanField(default=True),
        ),
    ]
