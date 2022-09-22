from rest_framework import serializers
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from decouple  import config

from .models import User




        
class UserSerializer(serializers.ModelSerializer): 
    
    class Meta:
        model = User
        # fields = ('__all__')
        exclude = ('is_active','is_verified','password','is_superuser','user_permissions','groups' )
          

class UserUpdateSerializer(serializers.ModelSerializer): 
    
    class Meta:
        model = User
        # fields = ('__all__')
        exclude = ('is_active','is_verified','password','is_superuser','user_permissions','groups' )
        

 
class GroupSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Group
        fields = ('name')

   
class UserRegistrationSerializer(serializers.Serializer):
    
    USER_MODE = (
        ('client', 'Client'),
        ('admin', 'Admin')
    )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    sex = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    phone= serializers.CharField(required=True)
    address = serializers.CharField(required=True)
    birth_date = serializers.DateField(required=True)
    user_mode = serializers.ChoiceField(required=True,choices=USER_MODE)
    
    class Meta:
        model = User
        fields = ('__all__')
        
        
    
    def create(self,validated_data):
        first_name = validated_data['first_name'] 
        last_name = validated_data['last_name'] 
        password = validated_data.pop('password') 
        email = validated_data['email'] 
        user_mode  = validated_data.pop('user_mode')
        
        is_user_exist = User.objects.filter(email=email).exists()
            
        if not is_user_exist:  
            if user_mode in ['admin','client']  :  
                validated_data['is_admin'] = True if user_mode == 'admin' else False     
                validated_data['username']= f'{first_name}_{last_name}'
                user = User.objects.create(**validated_data)
                user.set_password(password)    
                group,_= Group.objects.get_or_create(name=user_mode)
                user.is_verified=True  
                user.save()
                user.groups.add(group)
                
        else:
            raise serializers.ValidationError({'code': 400,
                                                'status':'error',
                                                'message': 'User already exist'})
       
            
        return validated_data

class LoginSerializer(serializers.Serializer):
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    
    
    def validate_new_password(self,value):
        validate_password(value)
        return value
    

class OTPVerificationSerializer(serializers.Serializer):
    otp_code = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    

class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
 
    
class ResetPasswordSerializer(serializers.Serializer):   
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
    
  
class ConfirmResetTokenSerializer (serializers.Serializer):
    otp_code = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

