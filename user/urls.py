from django.urls import path
from .views import UserLoginAPIView
from .views import UserRegisterAPIView
from .views import UserLogoutAPIView

urlpatterns = [
        path("login/", UserLoginAPIView.as_view(), name="user-login"),
        path("register/", UserRegisterAPIView.as_view(), name="user-register"),
        path("logout/", UserLogoutAPIView.as_view(), name="user-logout"),
        ]
