# Generated by Django 3.0.4 on 2021-06-11 16:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('teams_id', models.CharField(max_length=255, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Имя')),
                ('is_teacher', models.BooleanField(default=False, verbose_name='Является ли учителем')),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('teams_id', models.CharField(max_length=255, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название команды')),
                ('students', models.ManyToManyField(to='monitoring.Participant', verbose_name='Студенты')),
            ],
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('presentation', models.IntegerField(verbose_name='Продолжительность презентации')),
                ('microphone', models.IntegerField(verbose_name='Продолжительность включенного микрофона')),
                ('attendance', models.IntegerField(verbose_name='Продолжительность присутствия на занятии')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='settings', to='monitoring.Participant', verbose_name='Учитель')),
            ],
        ),
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('teams_id', models.CharField(max_length=255, verbose_name='ID')),
                ('students', models.ManyToManyField(to='monitoring.Participant', verbose_name='Студенты')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meetings', to='monitoring.Participant', verbose_name='Учитель')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meetings', to='monitoring.Team', verbose_name='Команда')),
            ],
        ),
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('presentation', models.IntegerField(default=0, verbose_name='Продолжительность презентации')),
                ('microphone', models.IntegerField(default=0, verbose_name='Продолжительность включенного микрофона')),
                ('attendance', models.IntegerField(default=0, verbose_name='Продолжительность присутствия на занятии')),
                ('meeting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='monitoring.Meeting', verbose_name='Встреча')),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actions', to='monitoring.Participant', verbose_name='Студент')),
            ],
        ),
    ]
