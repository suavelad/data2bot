from operator import mod
from django.db import models
from authentication.models import User


# Create your models here.

class Products(models.Model):
    id = models.AutoField(primary_key=True)
    sku = models.TextField(max_length=255,null=True,blank=True)
    name = models.TextField(null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    product_status = models.BooleanField(default=False)
    product_left = models.IntegerField( )
    price = models.FloatField(default=0.0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='product_creator')
    last_modified = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    time_created = models.TimeField(auto_now_add=True, null=True, blank=True)
    date_created = models.DateField(auto_now_add=True, null=True, blank=True)


class Order_history(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products,on_delete=models.CASCADE, related_name='product_order')
    quantity = models.IntegerField(null=True,blank=True)
    total_amount =  models.FloatField(null=True,blank=True)  
    client = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    last_modified = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    time_created = models.TimeField(auto_now_add=True, null=True, blank=True)
    date_created = models.DateField(auto_now_add=True, null=True, blank=True)



    





