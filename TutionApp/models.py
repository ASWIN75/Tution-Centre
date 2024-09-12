from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User

# Create your models here.
class CustomUser(AbstractUser):

    user_type=models.CharField(default=1,max_length=10)
    status=models.IntegerField(default=0)

class Course(models.Model):
    course_name = models.CharField(max_length=255)
    fee = models.IntegerField()
    course_duration = models.CharField(max_length=255)
    syllabus = models.FileField(upload_to='syllabus_pdfs/', null=True, blank=True)

    def __str__(self):
        return self.course_name
    
class Teacher(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    age=models.IntegerField()
    number=models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    image=models.ImageField(blank=True,upload_to='image/',null=True)

class Student(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,related_name='student_assignment')
    age=models.IntegerField()
    number=models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    image=models.ImageField(blank=True,upload_to='image/',null=True)
    teacher=models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True,related_name='teacher_assignment')

class Teacherattendance(models.Model):
    teacher_name=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    date=models.DateField()
    attendance=models.CharField(max_length=255)

class Studentattendance(models.Model):
    student_name=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    date=models.DateField()
    attendance=models.CharField(max_length=255)

class Task(models.Model):
    task_name=models.CharField(max_length=255)
    start_date=models.DateField()
    end_date=models.DateField()
    teacher=models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)

class Tasksubmit(models.Model):
    task=models.CharField(max_length=255)
    File=models.FileField(upload_to='task_pdfs/', null=True, blank=True)
    Description=models.CharField(max_length=255)
    student=models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)



