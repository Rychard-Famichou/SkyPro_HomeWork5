from django.urls import path

from users.views import CustomUserRetrieveUpdateAPIView, CustomUserCreateApiView


app_name = 'users'

urlpatterns = [
    path('create/', CustomUserCreateApiView.as_view(), name='user_create'),
    path('<int:pk>/', CustomUserRetrieveUpdateAPIView.as_view(),name='user_detail'),
]
