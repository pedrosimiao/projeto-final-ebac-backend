# hashtags/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import HashtagViewSet

router = DefaultRouter()
router.register(r'hashtags', HashtagViewSet)

urlpatterns = [
    path('', include(router.urls)),
]