from django.urls import path

from . import views

urlpatterns = [
    path('', views.feed, name='feed'),
    path('search/', views.search_view, name='search'),
    path('api/search/', views.search_api, name='search_api'),
    path('location/<str:location_name>/', views.location_view, name='location'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('api/notifications/', views.notifications_api, name='notifications_api'),
    path('api/notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),
]
