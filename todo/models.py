from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    pass

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    doer = models.ForeignKey(User,on_delete=models.CASCADE,related_name="categories",default=1)

    def __str__(self):
        return f"Category: {self.name}"

class Task(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length = 100)
    doer = models.ForeignKey(User,on_delete=models.CASCADE,related_name="tasks",default=1)
    category = models.ForeignKey(Category,blank=True,null=True,on_delete=models.SET_NULL,related_name="tasks")
    deadline = models.DateField(blank=True,null=True)
    complete = models.BooleanField(default=False)
    edit_mode = models.BooleanField(default=False)

    def __str__(self):
        return self.description

