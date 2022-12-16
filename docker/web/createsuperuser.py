from django.db import IntegrityError
from django.contrib.auth.models import User

import os # This package import from 'python-environ'


try:
    superuser = User.objects.create_superuser(
        username=os.getenv('SUPER_USER_NAME'),
        email=os.getenv('SUPER_USER_EMAIL'),
        password=os.getenv('SUPER_USER_PASSWORD'))
    superuser.save()
    print(f"Super User with username {os.getenv('SUPER_USER_NAME')} created!")
except IntegrityError:
    print(f"Super User with username {os.getenv('SUPER_USER_NAME')} already exit!")
except Exception as e:
    print(e)