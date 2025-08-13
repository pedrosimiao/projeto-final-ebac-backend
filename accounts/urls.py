# accounts/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .viewsets.user_viewset import UserViewSet
from .views import CustomTokenObtainPairView
from .views import SignUpView
from .views import ChangePasswordView
from .views import DeleteAccountView

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path(
        "login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("delete-account/", DeleteAccountView.as_view(), name="delete_account"),
    path("", include(router.urls)),
]
