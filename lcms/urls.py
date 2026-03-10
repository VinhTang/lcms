"""
URL configuration for lcms project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.shortcuts import render

urlpatterns = [
    path("", RedirectView.as_view(url="/accounts/login/", permanent=False), name="home"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("allauth.urls")),
    path("users/", include("users.urls", namespace="users")),
    path("", include("students.urls")),
    path("", include("classes.urls")),
    path("", include("attendance.urls")),
    path("", include("payments.urls")),
]

# Error Page Testing Routes (Visible even in DEBUG=True)
if settings.DEBUG:
    urlpatterns += [
        path("test-404/", lambda r: render(r, "404.html"), name="test-404"),
        path("test-500/", lambda r: render(r, "500.html"), name="test-500"),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom Error Handlers
handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'
