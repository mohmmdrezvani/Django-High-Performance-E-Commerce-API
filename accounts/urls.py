from django.urls import path
from .views import VerifyOTPView, SendOTPView
urlpatterns = [
    path('auth/send-otp', SendOTPView.as_view(), name='send-otp'),
    path('auth/verify_otp', VerifyOTPView.as_view(), name='verify-otp')
]
