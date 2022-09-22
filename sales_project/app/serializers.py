from rest_framework import serializers
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from rest_framework.generics import get_object_or_404
from decouple  import config

from .models import Products ,Order_history
from authentication.models import User



class ProductsSerializer(serializers.ModelSerializer): 
    
    class Meta:
        model = Products
        # fields = ('__all__')
        exclude = ['created_by','is_deleted' ]
 

class SingleOrderSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True)
    

class BulkOrderSerializer(serializers.Serializer):
    orders = SingleOrderSerializer(many=True)
    
    
    def create(self,validated_data):
        orders = validated_data['orders']
        request = self.context.get('request')
        user = request.user
        
        for order in orders:
            product_id = order['product_id']
            quantity = order['quantity']
            
            product = Products.objects.get(id=product_id)
            product_quantity_left = product.product_left
            price = product.price
            
            if product_quantity_left > 0 :
                total_amount = float(quantity *  price)
                Order_history.objects.create(client=user,product_id=product_id,quantity=quantity,total_amount=total_amount)
                product.product_left -= quantity
                product.save()
                return ({'status':'success','message':'Order Successful'})
            else:
                return ({'status':'failed','message':'Insufficient stock'})
  