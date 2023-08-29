from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.urls import reverse
from django.utils import timezone

from catalog.models import Position


class UserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        user = self._create_user(email, password, True, True, **extra_fields)
        user.save(using=self._db)
        return user


class Worker(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True, null=True, blank=True)
    position = models.ForeignKey(to=Position, on_delete=models.DO_NOTHING, null=True)
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=254, null=True, blank=True)
    last_name = models.CharField(max_length=254, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "Worker"
        verbose_name_plural = "Workers"
        ordering = ["position"]

    def __str__(self):
        if self.username:
            return self.username
        else:
            return self.email

    # def get_absolute_url(self):
    #     return "/users/%i/" % (self.pk) TODO: if new get_absolute_url dont work, change to it

    def get_absolute_url(self):
        return reverse(
            "catalog:profile_url_detail", args=[str(self.id)]
        )  # TODO: check url to profile
