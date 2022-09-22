from django.urls import path      
from rest_framework.routers import DefaultRouter
from .views import GetOrderHistoryView,BulkOrderView,ProductViewSet

router = DefaultRouter()

router.register('products',ProductViewSet, 'products')

urlpatterns = router.urls

urlpatterns += [
    path('get/order-history/', GetOrderHistoryView.as_view(), name="order-history"),
    path('make-order/', BulkOrderView.as_view(), name="make-order"),

]