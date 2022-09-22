
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet
from django.db.models import Q
from django.utils.decorators import  method_decorator
from django.shortcuts import get_object_or_404

from .serializers import UserSerializer, \
    UserRegistrationSerializer,LoginSerializer,ChangePasswordSerializer,\
        OTPVerificationSerializer,EmailSerializer,ResetPasswordSerializer,ConfirmResetTokenSerializer,\
            UserUpdateSerializer
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import authenticate, login, logout, get_user_model

from django.conf import settings

from .utils import  generateKey
import base64,pyotp

from django.core.mail import send_mail
from rest_framework.viewsets import ModelViewSet

from drf_spectacular.utils import (extend_schema, OpenApiExample)



class UserViewSet(ModelViewSet):
    
    queryset = User.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = UserSerializer
    
    def delete(self, request):
        user = request.user
        
        try:
            del_user = User.objects.get(id=user.id)
            del_user.is_deleted = True
            del_user.is_active = False
            del_user.save()
        
        except:
            return Response({'code':status.HTTP_400_BAD_REQUEST,
                                'status':'error',
                                'message':'User does not exist'},status=status.HTTP_400_BAD_REQUEST)
                

class CreateUserView(APIView):
    permission_classes= (AllowAny,) #For now, it is open

    @extend_schema(request=UserRegistrationSerializer)
    def post(self, request,*args,**kwargs):
        """
            Create a User
            ---
            parameters:
                - name: file
                  description: file
                  required: True
                  type: file
            responseMessages:
                - code: 201
                  message: Created
        """
                
        serializer = UserRegistrationSerializer(data=request.data)

        if  serializer.is_valid(): 
            result=serializer.save()
            email=result['email']            
            user = User.objects.get(email=email) 
            refresh = RefreshToken.for_user(user)
            
            #Send otp to user 
           
            user_exist = User.objects.filter(email=email,is_deleted=False, is_active=True).exists()
            if not user_exist :
                keygen = generateKey()
                key = base64.b32encode(keygen.returnValue(email).encode())
                OTP = pyotp.TOTP(key, interval=settings.OTP_TIMEOUT)
                print(OTP.now())
                subject = 'Profile Verification'
                message = f'Your verification OTP is {OTP.now()}. Please note, the otp expires in 5 minutes.'
                from_email = settings.EMAIL_HOST_USER
                to_list = [email]
                print(message)
                
                # Send OTP to user via email 
                # send_mail(subject, message, from_email, to_list, fail_silently=False)  #
                print("Kindly check your mail to reset your password") 
                return Response({'code':status.HTTP_201_CREATED,
                            'status':'success',
                            'message':'User created successfully, Check email for verification code',
                            'refresh': str(refresh),
                            'access': str(refresh.access_token),
                            'access_duration': settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
                            },status=status.HTTP_201_CREATED)
            else:
                return Response({
                        'code': status.HTTP_400_BAD_REQUEST,
                        'status':'error',
                        'message':'User with the email does not exist'
                        }, status=status.HTTP_400_BAD_REQUEST)
                      
        else:
            default_errors = serializer.errors
            print(default_errors)
            error_message = ''
            for field_name, field_errors in default_errors.items():
                error_message += f'{field_name} is {field_errors[0].code},'
            return Response({
                'code': status.HTTP_400_BAD_REQUEST,
                'status':'error',
                'message': error_message
                }, status=status.HTTP_400_BAD_REQUEST)
       

class LoginView(APIView):
    permission_classes=[AllowAny]
    authentication_classes=[]
    
    @extend_schema(request=LoginSerializer)
    def post(self,request):
        
        serializer= LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            try:
                user= User.objects.get(is_deleted=False,email=email)
                refresh = RefreshToken.for_user(user)
            except:
                return Response({'code':status.HTTP_400_BAD_REQUEST,
                                'status':'error',
                                'message':'User does not exist'},status=status.HTTP_400_BAD_REQUEST)
                
            if  not user.is_deleted:
                if  user.is_verified:
                    if user.is_active:
                            if user.check_password(password):
                                
                                
                                if user.groups.filter(Q(name='client')|Q(name='admin')).exists():
                                    the_serializer= UserUpdateSerializer #UserSerializer                                
                                    user_data = the_serializer(user).data

                                else:
                                    return Response({
                                        'code':status.HTTP_401_UNAUTHORIZED,
                                        'status':'error',
                                        'message':'User is not authorized. Kindly contact your admin'},status=status.HTTP_401_UNAUTHORIZED)
                                   
                                
                                return Response({
                                    'code':status.HTTP_200_OK,
                                    'status':'success',
                                    'message':'Login Sucessful',
                                    'user_info':user_data,
                                    'refresh': str(refresh),
                                    'access': str(refresh.access_token),
                                    'access_duration': settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
                                    },status=status.HTTP_200_OK)
                                    
                            else:
                                return Response({'code':status.HTTP_401_UNAUTHORIZED,
                                    'status':'error',
                                    'message':'Incorrect Password Inserted'},status=status.HTTP_401_UNAUTHORIZED)
                                    
                    else:
                        return Response({'code':status.HTTP_401_UNAUTHORIZED,
                            'status':'error',
                            'message':'User is not active. Kindly contact your admin'},status=status.HTTP_401_UNAUTHORIZED)
                                
                else:                   
                    
                    return Response({
                        'code':status.HTTP_406_NOT_ACCEPTABLE,
                        'status':'error',
                        'message':'User not verified.',
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'access_duration': settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']},status=status.HTTP_406_NOT_ACCEPTABLE)
            else:                   
                    
                    return Response({
                        'code':status.HTTP_400_BAD_REQUEST,
                        'status':'error',
                        'message':'User not found.',
                       },status=status.HTTP_400_BAD_REQUEST)
                

class UpdatePasswordView(APIView):

    @extend_schema(request=ChangePasswordSerializer)
    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            old_password = serializer.validated_data["old_password"]
            if not user.check_password(old_password):
                return Response({
                    'code':status.HTTP_400_BAD_REQUEST,
                    'status':"failed",
                    'message':"Incorrect Password"
                }, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response({
                'code':status.HTTP_200_OK,
                'status':"success",
                'message':"Password changed successfully"
            },status=status.HTTP_200_OK)
        default_errors = serializer.errors
        print(default_errors)
        error_message = ''
        for field_name, field_errors in default_errors.items():
            error_message += f'{field_name} is {field_errors[0].code},'
        return Response({
            'code':status.HTTP_400_BAD_REQUEST,
            'message': error_message
            }, status=status.HTTP_400_BAD_REQUEST)
        

class OTPVerificationView(APIView):
    permission_classes=[AllowAny]
    
    @extend_schema(request=OTPVerificationSerializer)
    def post(self, request):
        user = request.user
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            otp_code = serializer.validated_data['otp_code']
            email=serializer.validated_data['email']
            
            is_user_exist = User.objects.filter(email=email).exists()
            if  is_user_exist:
                user = User.objects.get(email=email)
                keygen = generateKey()
                key = base64.b32encode(keygen.returnValue(email).encode())  # Generating Key
                OTP = pyotp.TOTP(key, interval=settings.OTP_TIMEOUT)  # TOTP Model
                print(OTP.verify(otp_code))
                if OTP.verify(otp_code):
                    
                    user.is_verified = True
                    user.is_active = True
                    user.save()
                    login(request, user)
                    refresh = RefreshToken.for_user(user)
                    
   
                    if user.groups.filter(name='client').exists():
                        the_serializer= UserUpdateSerializer #UserSerializer
                        user_data = the_serializer(user).data
                    
                    elif user.groups.filter(name='admin').exists():
                        the_serializer= UserUpdateSerializer #UserSerializer
                        user_data = the_serializer(user).data
                       
                    else:
                        print ('User is not authorized')
                        return Response({'code':status.HTTP_401_UNAUTHORIZED,
                            'status':'error',
                            'message':'User is not authorized. Kindly contact your admin'},status=status.HTTP_401_UNAUTHORIZED)
                        
                    return Response({
                            'code':status.HTTP_200_OK,
                            'status':'success',
                            'message':'OTP verification successful',
                            'user_info':user_data,
                            'refresh': str(refresh),
                            'access': str(refresh.access_token),
                            'access_duration': settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
                            },status=status.HTTP_200_OK)
                        
                else:
                    return Response({
                        'code':status.HTTP_400_BAD_REQUEST,
                        'status': 'failed',
                        'message': 'OTP verification failed'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                        'code':status.HTTP_400_BAD_REQUEST,
                        'status': 'failed',
                        'message': 'User with the email does not exist'
                    }, status=status.HTTP_400_BAD_REQUEST)
        else:
            default_errors = serializer.errors
            print(default_errors)
            error_message = ''
            for field_name, field_errors in default_errors.items():
                error_message += f'{field_name} is {field_errors[0].code},'
            # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'code': 400,
                'message': error_message
                }, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordEmailView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(request=EmailSerializer)
    def post(self,request):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            email_address = serializer.data.get("email").lower()
            
            is_user_exist = User.objects.filter(email=email_address).exists()
            if is_user_exist:
                user = User.objects.get(email=email_address)
                refresh = RefreshToken.for_user(user)
                keygen = generateKey()
                key = base64.b32encode(keygen.returnValue(email_address).encode())
                OTP = pyotp.TOTP(key, interval=settings.OTP_TIMEOUT)
                otp_data= OTP.now()
                print(otp_data)
                subject = 'Reset Your Password'
                message = f'Your reset password OTP is {otp_data}. Please note, the otp expires in 5 minutes.'
                from_email = settings.EMAIL_HOST_USER
                to_list = [email_address]
                # send_mail(subject, message, from_email, to_list, fail_silently=False)
                print("Kindly check your mail to reset your password, otp is :",otp_data)
                return Response({
                    'code ': status.HTTP_200_OK,
                    'status':'Successful', 
                    'otp':f'{otp_data}', 
                    'otp_expiry': settings.OTP_TIMEOUT,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'access_duration': settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
                    },status=status.HTTP_200_OK)
            else:
                return Response({
                    'code': status.HTTP_400_BAD_REQUEST,
                    'message': 'User with the email does not exist'
                    }, status=status.HTTP_400_BAD_REQUEST)

        default_errors = serializer.errors
        error_message = ''
        for field_name, field_errors in default_errors.items():
            error_message += f'{field_name} is {field_errors[0].code},'
        return Response({
            'code': status.HTTP_400_BAD_REQUEST,
            'message': error_message
            }, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):

    @extend_schema(request=ResetPasswordSerializer)
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            password_1 = serializer.validated_data["password"]
            password_2 = serializer.validated_data["confirm_password"]
            if password_1 == password_2:
                user = User.objects.get(id=request.user.id)
                user.set_password(password_1)
                user.is_verified = True
                user.save()
                print(user)
                return Response({
                    'code':status.HTTP_200_OK,
                    'message':'User password changed successfully',
                    'resolve':'You can now proceed to login'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'code':'400',
                    'message':"Password don't match",
                    'resolve':'Ensure the two passwords are same'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            default_errors = serializer.errors
            print(default_errors)
            error_message = []
            for field_name, field_errors in default_errors.items():
                error_message.append(f'{field_name} is {field_errors[0].code}')
            # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            print(error_message)
            return Response({
                'code': 400,
                'message': ', '.join(error_message),
                'resolve': "Fix error in input"
                }, status=status.HTTP_400_BAD_REQUEST)
            
                            
class GetUserView(APIView):
    
    @extend_schema(responses = UserUpdateSerializer)
    def get(self,request):
        
        user=request.user
        if user:
            user = User.objects.get(email=user.email)
            refresh = RefreshToken.for_user(user)
            if user.is_verified:
                if user.is_active:
                        
                    
                    if  user.groups.filter(name='admin').exists():  
                        the_serializer= UserUpdateSerializer #UserSerializer
                        user_data = the_serializer(user).data
                    
                    elif user.groups.filter(name='user').exists():
                        the_serializer= UserUpdateSerializer #UserSerializer
                        user_data = the_serializer(user).data
                        
                    

                    else:
                        return Response({'code':401,
                            'status':'error',
                            'message':'User is not authorized. Kindly contact your admin'},status=status.HTTP_401_UNAUTHORIZED)
                
                    
                    return Response({
                        'code':status.HTTP_200_OK,
                        'status':'success',
                        'message':'User data gotten Sucessfully',
                        'user_info':user_data,
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'access_duration': settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
                        },status=status.HTTP_200_OK)
                        
                    
                else:
                    return Response({'code':401,
                        'status':'error',
                        'message':'User is not active. Kindly contact your admin'},status=status.HTTP_401_UNAUTHORIZED)
                            
            else:

                return Response({'code':401,
                    'status':'error',
                    'message':'User not verified.Kindly check your mail for your verification code',
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'access_duration': settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']},status=status.HTTP_401_UNAUTHORIZED)
                
        else:
            return Response({'code':401,
                            'status':'error',
                            'message':'User does not exist'},status=status.HTTP_401_UNAUTHORIZED)
