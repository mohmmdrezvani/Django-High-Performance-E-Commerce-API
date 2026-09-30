import time
from celery import shared_task


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def send_sms_task(self, phone_number, code):
    try:
        print(f"sending sms to {phone_number} with code {code} ...")
        time.sleep(1)
        return f"sms sent to {phone_number}"
    except Exception as exc:
        raise self.retry(exc=exc)

