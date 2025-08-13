# config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("__debug__/", include("debug_toolbar.urls")),
    path("api/", include("accounts.urls")),
    path("api/", include("posts.urls")),
    path("api/", include("comments.urls")),
    path("api/", include("notifications.urls")),
    path("api/likes/", include("likes.urls")),
    path("api/follows/", include("follows.urls")),
    path('api/', include('hashtags.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
