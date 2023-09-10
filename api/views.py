from rest_framework import generics, viewsets, mixins
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from api.permissions import IsOwnerOrAdminOrReadOnly
from user.models import Worker
from api.serializers import UserSerializer, UserCreateSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = (IsAdminUser,)


class UserView(
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)
    queryset = Worker.objects.all()


class SelfUserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Worker.objects

    def get_object(self):
        return self.request.user
