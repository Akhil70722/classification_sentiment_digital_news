"""
URL configuration for API endpoints.

This module defines all API routes for the News Intelligence & Alert System.
"""

from django.contrib import admin
from django.urls import path, include
from api import views

# URL patterns for API endpoints
urlpatterns = [
    # RESTful API endpoints using class-based views
    path('api/health/', views.HealthCheckView.as_view(), name='health_check'),
    path('api/categories/', views.CategoriesView.as_view(), name='get_categories'),
    path('api/news/', views.NewsListView.as_view(), name='get_news'),
    path('api/news/filter/', views.NewsFilterView.as_view(), name='filter_news'),
    
    # Legacy endpoint (for backward compatibility - function-based)
    path('', views.index, name='home')
]
