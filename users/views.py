from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics

from users.models import CustomUser, Payment
from users.serializers import CustomUserSerializer, PaymentSerializer

# Create your views here.
class CustomUserCreateApiView(generics.CreateAPIView):
    serializer_class = CustomUserSerializer


class CustomUserRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()


class PaymentCreateAPIView(generics.CreateAPIView):
   serializer_class = PaymentSerializer


class PaymentListAPIView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course', 'lesson', 'method']
    ordering_fields = ['date']
