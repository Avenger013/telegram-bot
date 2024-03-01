# Register your models here.

from django.contrib import admin
from .models import Teacher, Student


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'last_name', 'specialisation')

admin.site.register(Teacher, TeacherAdmin)


class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'tg_id', 'name', 'last_name', 'phone', 'teacher_id')

admin.site.register(Student, StudentAdmin)
