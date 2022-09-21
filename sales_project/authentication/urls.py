
from django.urls import path

        
from rest_framework.routers import DefaultRouter
 
router = DefaultRouter()


# router.register('users',UserViewSet, 'users')

urlpatterns = router.urls

urlpatterns += [
    # path('create/admin/', CreateAdminUserView.as_view(), name="create-admin"),

]