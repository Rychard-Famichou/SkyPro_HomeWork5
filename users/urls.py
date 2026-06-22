from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import CustomUserRetrieveAPIView, CustomUserCreateApiView, PaymentCreateAPIView, \
    PaymentListAPIView, CustomTokenObtainPairView, CustomUserUpdateAPIView, CustomUserDestroyAPIView, \
    CustomUserListAPIView, SubscriptionToggleAPIView

app_name = 'users'

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', CustomUserCreateApiView.as_view(), name='user_create'),
    path('list/', CustomUserListAPIView.as_view(), name='user_list'),
    path('<int:pk>/', CustomUserRetrieveAPIView.as_view(), name='user_detail'),
    path('<int:pk>/update/', CustomUserUpdateAPIView.as_view(), name='user_update'),
    path('<int:pk>/delete/', CustomUserDestroyAPIView.as_view(), name='user_delete'),
    path('payment/create/', PaymentCreateAPIView.as_view(), name='payment_create'),
    path('payment/list/', PaymentListAPIView.as_view(), name='payment_list'),
    path('subscription/toggle/', SubscriptionToggleAPIView.as_view(), name='subscription_toggle'),
]
