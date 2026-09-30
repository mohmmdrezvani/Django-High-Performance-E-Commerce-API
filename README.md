# Django High-Performance E-Commerce API

یک بک‌اند فروشگاهی مقیاس‌پذیر و آماده پروداکشن توسعه داده شده با فریم‌ورک Django و Django REST Framework.

## 🚀 ویژگی‌های کلیدی
- **احراز هویت**: سیستم OTP مبتنی بر Redis و توکن‌های JWT
- **پردازش پس‌زمینه**: تسک‌های ناهمگام با Celery، صف‌های Redis و داشبورد مانیتورینگ Flower
- **امنیت و تسویه حساب**: مدیریت اتمیک تراکنش‌ها (`select_for_update`) برای کنترل موجودی انبار
- **زیرساخت داکر**: کانتینریزاسیون کامل با Docker Compose، وب‌سرور Gunicorn و پراکسی معکوس Nginx
- **تست‌ها**: تست‌های خودکار سناریوهای بیزینس با Pytest

## 🛠️ راه‌اندازی سریع

1. متغیرهای محیطی را تنظیم کنید:
   ```bash
   cp .env.example .env
همچنین فایلی به نام **`.env.example`** کنار `.env` بساز و مقادیر حساس آن را با متون فرضی پر کن تا دیگران بدانند چه متغیرهایی لازم است.

---

### ۳. پایپ‌لاین خودکار تست روی گیت‌هاب (GitHub Actions CI)

برای اینکه هر بار کدی روی گیت‌هاب پوش شد، تست‌های Pytest به صورت خودکار اجرا شوند و در صورت بروز خطا به شما هشدار دهند، این پوشه و فایل را بساز:

مسیر: **`.github/workflows/ci.yml`**

```yaml
name: Django CI/CD Pipeline

on:
  push:
    branches: [ "main", "master" ]
  pull_request:
    branches: [ "main", "master" ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: shop_db
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
        options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5

      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: --health-cmd "redis-cli ping" --health-interval 10s --health-timeout 5s --health-retries 5

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: setup-python@v4
      with:
        python-version: '3.11'

    - name: Install Dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-django

    - name: Run Tests
      env:
        DB_NAME: shop_db
        DB_USER: postgres
        DB_PASSWORD: postgres
        DB_HOST: localhost
        DB_PORT: 5432
        REDIS_URL: redis://localhost:6379/1
      run: |
        pytest shop/tests.py