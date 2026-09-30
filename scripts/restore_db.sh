#!/bin/sh

if [-z "$1" ]; then
   echo "مسیر فایل پشتیبان را وارد کنید: ./scripts/restore_db.sh <backup_file.sql.gz>"
   exit 1
fi

BACKUP_FILE="$1"

echo "در حال بازیابی فایل پشتیبان..."
gunzip -c "$BACKUP_FILE" | docker compose exec -T db psql -U postgres shop_db

echo "پایگاه داده با موفقیت بازیابی شد."