# Django High-Performance E-Commerce API

یک بک‌اند فروشگاهی مقیاس‌پذیر و آماده پروداکشن توسعه داده شده با فریم‌ورک Django و Django REST Framework.

## 🚀 ویژگی‌های کلیدی
- **احراز هویت**: سیستم OTP مبتنی بر Redis و توکن‌های JWT
- **پردازش پس‌زمینه**: تسک‌های ناهمگام با Celery، صف‌های Redis و داشبورد مانیتورینگ Flower
- **امنیت و تسویه حساب**: مدیریت اتمیک تراکنش‌ها (`select_for_update`) برای کنترل موجودی انبار
- **زیرساخت داکر**: کانتینریزاسیون کامل با Docker Compose، وب‌سرور Gunicorn و پراکسی معکوس Nginx
- **تست‌ها**: تست‌های خودکار سناریوهای بیزینس با Pytest

## 🛠️ راه‌اندازی سریع

1. ایجاد فایل متغیرهای محیطی:
   ```bash
   cp .env.example .env

## 🌐 مسیرهای دسترسی
- **Swagger Docs:** `http://localhost/api/docs/`
- **Flower Dashboard:** `http://localhost:5555`