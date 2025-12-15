import uuid
from django.db import models


class User(models.Model):
    # id is created automatically as AutoField primary key (INT AUTO_INCREMENT)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)

    # Store hashed passwords (Django does this if you use AbstractUser; see note below)
    password = models.CharField(max_length=255)

    auth_token = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        app_label = "api"


class Login(models.Model):
    username = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        app_label = "api"


