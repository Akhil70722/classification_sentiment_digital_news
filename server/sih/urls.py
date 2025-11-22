"""
Main URL configuration for the sih project.

Routes URLs to views. For more information, see:
https://docs.djangoproject.com/en/4.1/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include

# Main URL patterns
urlpatterns = [
    # Django admin interface
    path('admin/', admin.site.urls),
    
    # API endpoints (includes all routes from api.urls)
    path('', include('api.urls'))
]
