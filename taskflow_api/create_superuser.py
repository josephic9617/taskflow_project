import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskflow_api.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = 'admin'
password = 'admin'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email='admin@example.com', password=password)
    print(f"Superuser '{username}' created with password '{password}'")
else:
    print(f"Superuser '{username}' already exists")
