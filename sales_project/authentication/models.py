from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    SEX = (
        ('m', 'Male'),
        ('f', 'Female')
    )
    username = models.CharField(max_length=250, unique=True)
    email = models.EmailField(max_length=250, unique=True)
    is_deleted = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False, blank=True, null=True)
    is_active = models.BooleanField(default=False, blank=True)
    is_verified = models.BooleanField(default=False, blank=True)
    sex = models.CharField(max_length=7, choices=SEX, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    last_modified = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    time_created = models.TimeField(auto_now_add=True, null=True, blank=True)
    date_created = models.DateField(auto_now_add=True, null=True, blank=True)


