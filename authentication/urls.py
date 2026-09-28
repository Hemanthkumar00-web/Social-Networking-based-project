from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('password-reset-sent/', views.password_reset_sent, name='password_reset_sent'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
]
