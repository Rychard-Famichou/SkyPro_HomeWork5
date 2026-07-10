from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.views import TokenObtainPairView

from materials.models import Course
from users.models import CustomUser, Payment, Subscription
from users.permissions import IsOwner, IsSelf
from users.serializers import (
    CustomTokenObtainPairSerializer,
    CustomUserSerializer,
    PaymentSerializer,
    PublicUserSerializer,
    SubscriptionSerializer,
)
from users.services import (
    create_stripe_checkout_session,
    create_stripe_price,
    create_stripe_product,
    retrieve_stripe_checkout_session,
)


# Create your views here.
class CustomTokenObtainPairView(TokenObtainPairView):
    """Create a new token for our user"""

    serializer_class = CustomTokenObtainPairSerializer


class CustomUserCreateApiView(generics.CreateAPIView):
    """Create a new user in the system"""

    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]


class CustomUserRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve a user from the system"""

    queryset = CustomUser.objects.all()

    def get_serializer_class(self):
        if getattr(self, "swagger_fake_view", False):
            return CustomUserSerializer

        user_pk = self.kwargs.get("pk")

        if self.request.user.is_authenticated and self.request.user.pk == int(user_pk):
            return CustomUserSerializer

        return PublicUserSerializer


class CustomUserListAPIView(generics.ListAPIView):
    """List all users in the system"""

    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()


class CustomUserUpdateAPIView(generics.UpdateAPIView):
    """Update a user from the system"""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsSelf]


class CustomUserDestroyAPIView(generics.DestroyAPIView):
    """Delete a user from the system"""

    queryset = CustomUser.objects.all()
    permission_classes = [IsSelf]


class PaymentCreateAPIView(generics.CreateAPIView):
    """Create a new payment"""

    serializer_class = PaymentSerializer

    def perform_create(self, serializer):
        course = serializer.validated_data.get("course")
        lesson = serializer.validated_data.get("lesson")

        if course:
            product_title = course.title
            amount = course.price
        else:
            product_title = lesson.title
            amount = lesson.price

        stripe_product_id = create_stripe_product(product_title)
        stripe_price_id = create_stripe_price(stripe_product_id, amount)
        stripe_session = create_stripe_checkout_session(stripe_price_id)

        serializer.save(
            owner=self.request.user,
            amount=amount,
            method="TRANSFER",
            stripe_session_id=stripe_session.id,
            link=stripe_session.url,
        )


class PaymentListAPIView(generics.ListAPIView):
    """List all payments"""

    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["course", "lesson", "method"]
    ordering_fields = ["date"]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(owner=user)


class PaymentDetailAPIView(generics.RetrieveAPIView):
    """Retrieve a payment"""

    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsOwner]

    def get_object(self):
        obj = super().get_object()
        session_id = obj.stripe_session_id

        if session_id:
            new_status = retrieve_stripe_checkout_session(session_id)
            obj.status = new_status
            obj.save()

        return obj


class SubscriptionToggleAPIView(APIView):
    """Toggle a subscription"""

    def post(self, request, *args, **kwargs):
        serializer = SubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course_id = serializer.validated_data["course_id"]
        user = request.user
        course = Course.objects.get(pk=course_id)

        subscription, created = Subscription.objects.get_or_create(owner=user, course=course)

        if created:
            return Response(
                {"message": f"Подписка на курс {course} успешно добавлена."},
                status=status.HTTP_201_CREATED,
            )
        else:
            subscription.delete()
            return Response(
                {"message": f"Подписка на курс {course} успешно удалена."},
                status=status.HTTP_200_OK,
            )
