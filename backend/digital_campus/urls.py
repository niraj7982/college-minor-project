"""
URL configuration for digital_campus project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core import views as core_views

urlpatterns = [
    path('admin/dashboard/', core_views.admin_dashboard, name='admin_dashboard'),
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

from django.conf import settings
from django.views.static import serve
from django.urls import re_path
from django.http import Http404

def vercel_media_serve(request, path, document_root=None, **kwargs):
    try:
        return serve(request, path, document_root=document_root, **kwargs)
    except Http404:
        fallback_root = settings.BASE_DIR / 'media'
        if str(document_root) != str(fallback_root):
            try:
                return serve(request, path, document_root=fallback_root, **kwargs)
            except Http404:
                pass
        raise

if settings.DEBUG or getattr(settings, 'IS_VERCEL', False):
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', vercel_media_serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]


