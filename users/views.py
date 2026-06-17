from rest_framework import generics

from users.models import CustomUser
from users.serializers import CustomUserSerializer


# Create your views here.
class CustomUserCreateApiView(generics.CreateAPIView):
    serializer_class = CustomUserSerializer


class CustomUserRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
