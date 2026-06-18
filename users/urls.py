from django.urls import path

from users.views import CustomUserRetrieveUpdateAPIView, CustomUserCreateApiView, PaymentCreateAPIView, \
    PaymentListAPIView

app_name = 'users'

urlpatterns = [
    path('create/', CustomUserCreateApiView.as_view(), name='user_create'),
    path('<int:pk>/', CustomUserRetrieveUpdateAPIView.as_view(),name='user_detail'),
    path('payment/create/', PaymentCreateAPIView.as_view(), name='payment_create'),
    path('payment/list/', PaymentListAPIView.as_view(), name='payment_list'),
]
