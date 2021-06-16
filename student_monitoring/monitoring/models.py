from django.db import models


class Participant(models.Model):
    teams_id = models.CharField(verbose_name="ID", max_length=255)
    name = models.CharField(verbose_name="Имя", max_length=255)
    is_teacher = models.BooleanField(verbose_name="Является ли учителем", default=False)


class Team(models.Model):
    teams_id = models.CharField(verbose_name="ID", max_length=255)
    name = models.CharField(verbose_name="Название команды", max_length=255)
    students = models.ManyToManyField(Participant, verbose_name="Студенты")


class Settings(models.Model):
    owner = models.ForeignKey(verbose_name="Учитель", to='Participant', related_name='+', on_delete=models.CASCADE)
    team = models.ForeignKey(verbose_name="Группа", to='Team', related_name='settings', on_delete=models.CASCADE)
    teacher_presentation = models.IntegerField(verbose_name="Продолжительность презентации учителя")
    student_presentation = models.IntegerField(verbose_name="Продолжительность презентации студента")
    microphone = models.IntegerField(verbose_name="Продолжительность включенного микрофона")
    attendance = models.IntegerField(verbose_name="Продолжительность присутствия на занятии")
    allow_to_miss = models.IntegerField(verbose_name="Количество допустимых пропусков")
    active_percent = models.IntegerField(verbose_name="Процент выполнения")
    start = models.DateField(verbose_name="Начало семестра")
    end = models.DateField(verbose_name="Конец семестра")


class Meeting(models.Model):
    teams_id = models.CharField(verbose_name="ID", max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    teacher = models.ForeignKey(verbose_name="Учитель", to='Participant', related_name='meetings', on_delete=models.CASCADE)
    team = models.ForeignKey(verbose_name="Команда", to='Team', related_name='meetings', on_delete=models.CASCADE)
    students = models.ManyToManyField(Participant, verbose_name="Студенты")


class Action(models.Model):
    participant = models.ForeignKey(verbose_name="Студент", to='Participant', related_name='actions', on_delete=models.CASCADE)
    meeting = models.ForeignKey(verbose_name="Встреча", to='Meeting', related_name='+', on_delete=models.CASCADE)
    presentation = models.IntegerField(verbose_name="Продолжительность презентации", default=0)
    microphone = models.IntegerField(verbose_name="Продолжительность включенного микрофона", default=0)
    attendance = models.IntegerField(verbose_name="Продолжительность присутствия на занятии", default=0)
