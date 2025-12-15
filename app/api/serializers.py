from rest_framework import serializers
from .models import User, Login


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "auth_token",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Login
        fields = [
            "id",
            "username",
            "email",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
