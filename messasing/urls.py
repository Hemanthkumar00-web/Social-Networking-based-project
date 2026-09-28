from django.urls import path

from . import views

urlpatterns = [
    path('messages/', views.inbox, name='messages_inbox'),
    path('messages/new/', views.new_message, name='new_message'),
    path('messages/<str:username>/', views.chat, name='chat'),
    path('messages/<str:username>/send/', views.send_message, name='send_message'),
    path('messages/unsend/<int:pk>/', views.unsend_message, name='unsend_message'),
]
