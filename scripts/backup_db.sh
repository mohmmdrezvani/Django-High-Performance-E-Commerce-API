#!/bin/sh

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/shop_db_${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"

echo "در حال ایجاد فایل پشتیبان از پایگاه داده..."
docker compose exec -T db pg_dump -U postgres shop_db | gzip > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "پشتیبان‌گیری با موفقیت در مسیر زیر انجام شد:"
    echo "$BACKUP_FILE"
    # حذف نسخه‌های قدیمی‌تر از ۷ روز
    find "$BACKUP_DIR" -type f -name "*.sql.gz" -mtime +7 -exec rm {} \;
else
    echo "خطا در عملیات پشتیبان‌گیری دیتابیس!"
    exit 1
fi