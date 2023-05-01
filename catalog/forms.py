from django.contrib.auth.forms import  AuthenticationForm

from .models import Worker


class LoginForm(AuthenticationForm):
    class Meta:
        model = Worker
