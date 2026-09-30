from rest_framework import serializers
from django.core.validators import RegexValidator

from shop.models import Category , Product,ProductImage

phone_validator = RegexValidator(
    regex=r'^09\d{9}$', message='فرمت شماره موبایل معتبر نیست.')


class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(validators=[phone_validator])


class VerifyOTPSerializer(serializers.Serializer):
    def __init__(self, instance=None, data=None, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.validate_data = None

    phone_number = serializers.CharField(validators=[phone_validator])
    code = serializers.CharField(max_length=5, min_length=5)
