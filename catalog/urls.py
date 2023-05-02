from django.contrib.auth.views import LogoutView
from django.urls import path

from catalog.views import (
    index,
    LoginView,
    SignUpView,
)

urlpatterns = [
    path("", index, name="index"),
    path("login/", LoginView.as_view(), name="login"),
    path("registrate/", SignUpView.as_view(), name="registrate"),
    path('logout/', LogoutView.as_view(next_page='catalog:index'), name='logout')
]

app_name = 'catalog'
