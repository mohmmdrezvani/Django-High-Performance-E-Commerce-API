import random
from django.core.cache import cache
from .tasks import send_sms_task

def generate_and_save_otp(phone_number):
    otp_code = str(random.randint(1000, 99999))

    cache_key = f"otp:{phone_number}"
    cache.set(cache_key, otp_code, timeout=120)
    print(f"\n=============================")
    print(f" OTP for {phone_number}: {otp_code}")
    print(f"=============================\n")
    send_sms_task.delay(phone_number,otp_code)
    return otp_code


def verify_otp(phone_number, code):
    cache_key = f"otp:{phone_number}"
    saved_code = cache.get(cache_key)

    if saved_code and saved_code == code:
        cache.delete(cache_key)
        return True
    return False
