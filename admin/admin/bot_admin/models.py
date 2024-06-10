# Create your models here.

# ваше_приложение/models.py

from django.db import models
from datetime import datetime


class Teacher(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    specialisation = models.CharField(max_length=255)
    password_teacher = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'teachers'

    def __str__(self):
        return f"{self.name} {self.last_name}"


class Student(models.Model):
    id = models.IntegerField(primary_key=True)
    tg_id = models.BigIntegerField()
    date_of_registration = models.DateTimeField(default=datetime.now)
    name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    specialisation_student = models.CharField(max_length=255, null=True, blank=True)
    point = models.IntegerField(null=True, blank=True)

    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='students', db_column='teacher_id')

    class Meta:
        managed = False
        db_table = 'students'

    def __str__(self):
        return f"{self.name} {self.last_name}"
