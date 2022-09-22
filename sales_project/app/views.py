import requests
from django.db.models import Q
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import Order_history,Products
from .serializers import BulkOrderSerializer,ProductsSerializer
from authentication.utils import CustomPagination
from drf_spectacular.utils import (extend_schema,OpenApiParameter,OpenApiTypes)




# Create your views here.

class ProductViewSet(ModelViewSet):
    
    queryset = Products.objects.filter(Q(is_deleted=False)| Q(product_status=True)|  Q(product_left__gte=0)).order_by('-id')
    serializer_class = ProductsSerializer
    
    def delete(self, request):
        user = request.user
        
        try:
            del_user = Products.objects.get(created_by=user)
            del_user.is_deleted = True
            del_user.is_active = False
            del_user.save()
        
        except:
            return Response({'code':status.HTTP_400_BAD_REQUEST,
                                'status':'error',
                                'message':'You can only delete your product'},status=status.HTTP_400_BAD_REQUEST)
    
    
class BulkOrderView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BulkOrderSerializer
    
    @extend_schema(request= BulkOrderSerializer)
    def post(self,request):
        serializer = BulkOrderSerializer(data=request.data, context = {'request':request})
        
        if serializer.is_valid():
            result = serializer.save()
            
            return Response({
                    'code':status.HTTP_200_OK if result['status'] == 'success' else status.HTTP_400_BAD_REQUEST,
                    'status':result['status'],
                    'message':result['message']},status=status.HTTP_200_OK if result['status'] == 'success' else status.HTTP_400_BAD_REQUEST)

        else:
            default_errors = serializer.errors
            error_messages = ''
            for field_name , field_errors in default_errors.items():
                error_messages += f'{field_name} is {field_errors[0].code}'
            
            return Response({
                    'code': status.HTTP_400_BAD_REQUEST,
                    'status':'error',
                    'message':error_messages,
                    }, status=status.HTTP_400_BAD_REQUEST)
            
class GetOrderHistoryView(APIView):
    permission_classes = (IsAuthenticated,)
    
    @extend_schema(
            parameters=[
            OpenApiParameter("start_date", OpenApiTypes.DATETIME, OpenApiParameter.QUERY),
            OpenApiParameter("end_date", OpenApiTypes.DATETIME, OpenApiParameter.QUERY), # path variable was overridden
            ],
           
    )    
    def get(self, request):
        user =request.user
        user_group = request.user.groups.all()[0].name
        print(user_group)
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        queryset = Order_history.objects.filter()
        if start_date:
            queryset= queryset.filter(start_date = start_date)
        if end_date:
            queryset= queryset.filter(end_date = end_date)
               
        if user_group == 'client':
            queryset= queryset.filter(client =user)
        elif user_group == 'admin':   
            queryset = queryset
        else:
            return Response({
                    'code': status.HTTP_400_BAD_REQUEST,
                    'status':'error',
                    'message':'User is not authorized'
                    }, status=status.HTTP_400_BAD_REQUEST)
                 
        if not queryset:
            return Response({
                        'code': status.HTTP_400_BAD_REQUEST,
                        'status':'error',
                        'message':'No data'
                        }, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            output = queryset.values('client__last_name','client__first_name','product__sku','product__name','quantity','total_amount','date_created','time_created')
          
            return Response({
                        'code': status.HTTP_200_OK,
                        'status':'success',
                        'data':output
                        }, status=status.HTTP_200_OK)
            
            return (serializer.data)
            