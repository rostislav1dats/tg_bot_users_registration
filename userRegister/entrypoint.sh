#!/bin/bash

echo "Waiting for postgres..."
sleep 5
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

python manage.py makemigrations
python manage.py migrate

echo "Creating superuser..."
python manage.py shell << END
from django.contrib.auth import get_user_model
import os

User = get_user_model()
username = "alex"
password = "qwerty12345@"
email = "alex@ukr.net"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"--- Superuser '{username}' created successfully ---")
else:
    user = User.objects.get(username=username)
    user.set_password(password)
    user.save()
    print(f"--- Superuser '{username}' already exists. Password updated. ---")
END

python manage.py set_webhooks

exec gunicorn userRegister.asgi:application \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
