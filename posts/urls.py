from django.urls import path

from . import views

urlpatterns = [
    path('posts/create/', views.create_post, name='create_post'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('posts/<int:pk>/like/', views.like_post, name='like_post'),
    path('posts/<int:pk>/comment/', views.comment_post, name='comment_post'),
    path('posts/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('posts/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('posts/<int:pk>/save/', views.save_post, name='save_post'),
    path('stories/create/', views.create_story, name='create_story'),
    path('stories/<str:username>/view/', views.view_stories, name='view_stories'),
    path('stories/my/', views.user_stories_list, name='user_stories_list'),
    path('highlights/create/', views.create_highlight, name='create_highlight'),
    path('highlights/<int:pk>/edit/', views.edit_highlight, name='edit_highlight'),
    path('highlights/<int:pk>/delete/', views.delete_highlight, name='delete_highlight'),
    path('highlights/<int:pk>/stories/', views.highlight_stories, name='highlight_stories'),
    path('reels/', views.reels_view, name='reels'),
    path('reels/create/', views.create_reel, name='create_reel'),
    path('reels/<int:pk>/like/', views.like_reel, name='like_reel'),
    path('reels/<int:pk>/delete/', views.delete_reel, name='delete_reel'),
    path('reels/<int:pk>/comment/', views.comment_reel, name='comment_reel'),
    path('reels/<int:pk>/comments/', views.reel_comments, name='reel_comments'),
    path('reels/<int:pk>/save/', views.save_reel, name='save_reel'),
    path('reels/<int:pk>/repost/', views.repost_reel, name='repost_reel'),
    path('songs/search/', views.search_songs, name='search_songs'),
]
