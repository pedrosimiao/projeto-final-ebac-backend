# notifications/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MarkAllAsReadView
from .viewsets import NotificationViewSet

router = DefaultRouter()
router.register(r"notifications", NotificationViewSet, basename="notifications")

urlpatterns = [
    path("", include(router.urls)),
    path("mark_all_as_read/", MarkAllAsReadView.as_view(), name="mark-all-as-read"),
]
