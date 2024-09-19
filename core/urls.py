"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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

from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from django.conf.urls.static import static  # Used for static files

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),

    # Include other app-specific URL patterns
    path('', include('homepage.urls')),
    path('inventory/', include('inventory.urls')),
    path('transaction/', include('transaction.urls')),
]

# Serve media files (user-uploaded files)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve static files (CSS, JavaScript, etc.)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
