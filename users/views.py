from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from materials.models import Course
from users.models import CustomUser, Payment, Subscription
from users.permissions import IsSelf, IsOwner
from users.serializers import CustomUserSerializer, PaymentSerializer, CustomTokenObtainPairSerializer, \
    PublicUserSerializer, SubscriptionSerializer


# Create your views here.
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomUserCreateApiView(generics.CreateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]


class CustomUserRetrieveAPIView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()

    def get_serializer_class(self):
        requested_user = self.get_object()

        if self.request.user == requested_user:
            return CustomUserSerializer

        return PublicUserSerializer


class CustomUserListAPIView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()


class CustomUserUpdateAPIView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsSelf]


class CustomUserDestroyAPIView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [IsSelf]


class PaymentCreateAPIView(generics.CreateAPIView):
    serializer_class = PaymentSerializer

    def perform_create(self, serializer):
        if self.request.user.is_anonymous:
            raise NotAuthenticated("Пользователь не авторизован.")
        serializer.save(owner=self.request.user)


class PaymentListAPIView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course', 'lesson', 'method']
    ordering_fields = ['date']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(owner=user)


class SubscriptionToggleAPIView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = SubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course_id = serializer.validated_data['course_id']
        user = request.user
        course = Course.objects.get(pk=course_id)

        subscription, created = Subscription.objects.get_or_create(
            owner=user,
            course=course
        )

        if created:
            return Response(
                {"message": f"Подписка на курс {course} успешно добавлена."},
                status=status.HTTP_201_CREATED
            )
        else:
            subscription.delete()
            return Response(
                {"message": f"Подписка на курс {course} успешно удалена."},
                status=status.HTTP_200_OK
            )
