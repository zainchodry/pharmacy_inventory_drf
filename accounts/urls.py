from django.urls import path
from . views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView



urlpatterns = [
    path('register', RegisterView.as_view(), name = 'register'),
    path('login', TokenObtainPairView.as_view(), name = 'login'),
    path('refresh', TokenRefreshView.as_view(), name = 'refresh'),
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user_detail"),
    path("users/<int:pk>/promote/", PromoteUserView.as_view(), name="user_promote"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
]
