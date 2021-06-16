# Generated by Django 3.0.4 on 2021-06-11 18:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='team',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='settings', to='monitoring.Team', verbose_name='Группа'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='settings',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='monitoring.Participant', verbose_name='Учитель'),
        ),
    ]
