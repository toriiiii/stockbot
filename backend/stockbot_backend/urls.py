from django.urls import path, include, re_path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import re

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/inventory/", include("inventory.urls")),

    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
] 