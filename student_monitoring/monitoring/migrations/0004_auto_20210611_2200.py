# Generated by Django 3.0.4 on 2021-06-11 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0003_auto_20210611_1859'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='end_time',
            field=models.DateTimeField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='meeting',
            name='start_time',
            field=models.DateTimeField(default=None),
            preserve_default=False,
        ),
    ]
