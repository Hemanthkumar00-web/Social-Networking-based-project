from django.urls import path

from . import views

urlpatterns = [
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/settings/', views.settings_view, name='settings'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('profile/<str:username>/follow/', views.follow_toggle, name='follow_toggle'),
    path('profile/<str:username>/remove-follower/', views.remove_follower, name='remove_follower'),
    path('profile/<str:username>/followers/', views.followers_list, name='followers_list'),
    path('profile/<str:username>/following/', views.following_list, name='following_list'),
]
