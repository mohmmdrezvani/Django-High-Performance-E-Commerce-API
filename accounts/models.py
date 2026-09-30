from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from .managers import UserManager

# Create your models here.


phone_regex = RegexValidator(
    regex=r'^09/d{9}$',
    message='شماره موبایل باید با09 شروع شده و 11 رقم باشد.'
)


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=11, unique=True, validators=[
        phone_regex], verbose_name='شماره موبایل')
    first_name = models.CharField(max_length=50, blank=True, )
    last_name = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone_number
