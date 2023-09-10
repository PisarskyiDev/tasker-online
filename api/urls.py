from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from api.views import CreateUserView, UserView, SelfUserProfileView

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create_profile"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path(
        "profile/all/", UserView.as_view({"get": "list"}), name="all_profile"
    ),
    path("profile/me/", SelfUserProfileView.as_view(), name="my_profile"),
]

app_name = "api"