from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "position",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
            "is_active",
            "last_login",
            "date_joined",
            "waiting_verified",
        )
        read_only_fields = ("is_staff", "waiting_verified", "is_active")
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 5,
                "required": False,
            }
        }

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, set the password and avatar correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)

        user.save()

        return user


class UserCreateSerializer(UserSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "password",
        )
        read_only_fields = ("is_staff",)
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 5,
                "required": False,
            }
        }
