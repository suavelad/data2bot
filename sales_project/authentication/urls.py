
from django.urls import path
from .views import UserViewSet,CreateUserView,LoginView,UpdatePasswordView,OTPVerificationView,\
    ResetPasswordEmailView,ResetPasswordView,GetUserView
from rest_framework.routers import DefaultRouter
 
router = DefaultRouter()


router.register('users',UserViewSet, 'users')

urlpatterns = router.urls

urlpatterns += [
    path('create/user/', CreateUserView.as_view(), name="create-user"),
    path('login/', LoginView.as_view(), name="create-user"),
    path('password-update/', UpdatePasswordView.as_view(), name="password-update"),
    path('verify-otp/', OTPVerificationView.as_view(), name="verify-otp"),
    path('reset-password-email/', ResetPasswordEmailView.as_view(), name="reset-passsword-email"),
    path('reset-password/', ResetPasswordView.as_view(), name="reset-password"),
    path('get-profile/', GetUserView.as_view(), name="reset-password"),


]