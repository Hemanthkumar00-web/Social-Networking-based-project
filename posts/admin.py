from django.contrib import admin

from .models import Comment, Highlight, Post, Reel, ReelComment, Song, Story


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'genre', 'plays', 'created_at')
    list_filter = ('genre',)
    search_fields = ('title', 'artist')
    ordering = ('-created_at',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'pk', 'created_at')
    list_filter = ('created_at',)


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'pk', 'created_at')


@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'created_at')


@admin.register(Reel)
class ReelAdmin(admin.ModelAdmin):
    list_display = ('user', 'pk', 'created_at')


admin.site.register(Comment)
admin.site.register(ReelComment)
