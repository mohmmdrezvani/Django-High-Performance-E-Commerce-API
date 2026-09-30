from drf_spectacular.utils import extend_schema
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import SendOTPSerializer, VerifyOTPSerializer
from .services import generate_and_save_otp, verify_otp


# Create your views here.


class OTPThrottle(SimpleRateThrottle):
    scope = 'otp_request'
    def get_cache_key(self, request, view):
        phone = request.data.get('phone_number')
        if phone:
            return f"throttle_otp_{phone}"
        return self.get_ident(request)

class SendOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [OTPThrottle]

    @extend_schema(request=SendOTPSerializer, responses={200: dict})
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone_number']

        generate_and_save_otp(phone)
        return Response({'detail': 'کد تایید ارسال شد.'}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=VerifyOTPSerializer, responses={200: dict})
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone_number']
        code = serializer.validated_data['code']

        if not verify_otp(phone, code):
            return Response({'detail': 'کد اشتباه است یا منقضی شده.'}, status=status.HTTP_400_BAD_REQUEST)

        user, _ = User.objects.get_or_create(phone_number=phone)
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)

