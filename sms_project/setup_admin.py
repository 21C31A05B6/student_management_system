#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sms_project.settings')
django.setup()

from accounts.models import User

# Create admin user
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser(
        username='admin',
        email='admin@test.com',
        password='admin123',
        role='ADMIN'
    )
    print(f"✓ Created admin user: {user.username}")
else:
    print("✓ Admin user already exists")

print(f"✓ Total users: {User.objects.count()}")
print("\n📝 Login Credentials:")
print("   Username: admin")
print("   Password: admin123")
