from rest_framework import generics, viewsets, mixins
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from rest_framework.response import Response
from user.models import Worker
from api.serializers import UserSerializer, UserCreateSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = (IsAdminUser,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Получите значение email из validated_data
        email = serializer.validated_data["email"]

        # Если username отсутствует в исходных данных, сгенерируйте его
        if "username" not in serializer.validated_data:
            username = email.split("@")[0]
            serializer.validated_data["username"] = username

        # Вызывайте .save() после генерации username
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


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
